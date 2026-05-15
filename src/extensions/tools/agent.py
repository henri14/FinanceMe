import json
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

load_dotenv()

Path("data").mkdir(exist_ok=True)
logger.add(
    "data/copilot_traces.jsonl",
    filter=lambda r: r["name"].startswith("src.extensions.tools.agent"),
    serialize=True,
    rotation="10 MB",
    retention=5,
)

from src.core.config import load_config
from src.extensions.rag.retriever import Retriever
from src.extensions.tools.models import AgentPlan
from src.extensions.tools.tool_schemas import TOOL_SCHEMAS
from src.tools.calendar_tool import get_next_slot
from src.tools.crm import get_application

_SYSTEM_PROMPT = """You are an Operations Copilot for Acme FinanceMe, assisting the operations \
team in NSW, Australia with loan application queries.

RULES — follow these without exception:
1. Use ONLY data returned by the tools. Never invent facts, dates, or policy clauses.
2. If an application cannot be found in the CRM, you MUST set AgentStatus to \
"requires human intervention" and explain why in AgentReasoning.
3. Respect the customer's contact_preferences when recommending communication actions.
4. Never recommend actions that would violate Acme policy or ASIC / NCCP regulations.
5. Reference only masked customer identifiers in your reasoning \
(customer_name_masked, account_last4). Never write out full names, dates of birth, \
or full account numbers.
6. If the query falls outside what company policy permits, or the necessary facts \
are unavailable, set AgentStatus to "requires human intervention".

WORKFLOW:
- Call lookup_application first to retrieve the application.
- Call search_policy for any relevant SLA, escalation, or regulatory questions.
- Call get_next_slot if a follow-up appointment needs to be scheduled.
- Once you have enough information, produce your final structured plan.

OUTPUT FORMAT:
Respond with a JSON object matching exactly this schema:
{
  "ApplicationId": "<app_id>",
  "AgentStatus": "plan generated" | "requires human intervention",
  "AgentReasoning": "<step-by-step reasoning, PII-safe>",
  "PlanText": "<plain-English action plan for the ops team>"
}
"""


class CopilotAgent:
    MAX_STEPS = 10

    def __init__(self) -> None:
        self.config = load_config()
        self.client = OpenAI(api_key=self.config.api_key)
        self.retriever = Retriever()

    def run(self, app_id: str, question: str) -> AgentPlan:
        log = logger.bind(app_id=app_id)
        log.info("copilot started")

        messages: list = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Application ID: {app_id}\n"
                    f"Question: {question}\n\n"
                    "Please investigate and produce an action plan."
                ),
            },
        ]

        for step in range(self.MAX_STEPS):
            log.info(f"step {step}: calling model")
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
            choice = response.choices[0]
            messages.append(choice.message)

            if choice.finish_reason == "stop":
                log.info(f"step {step}: model finished")
                break

            if choice.finish_reason == "tool_calls":
                for tc in choice.message.tool_calls:
                    result = self._dispatch(tc, log)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    })
        else:
            log.warning("max steps reached without completion")
            return AgentPlan(
                ApplicationId=app_id,
                AgentStatus="requires human intervention",
                AgentReasoning="Agent reached maximum reasoning steps without producing a plan.",
                PlanText="Escalate to a senior operator for manual review.",
            )

        return self._extract_plan(app_id, messages, log)

    def _dispatch(self, tool_call, log) -> object:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        log.info(f"tool call: {name} args={list(args.keys())}")

        if name == "lookup_application":
            app = get_application(args["app_id"])
            if app is None:
                return {"error": f"Application {args['app_id']} not found in CRM"}
            return app.to_dict()

        if name == "search_policy":
            chunks, latency_ms = self.retriever.query(args["query"])
            log.info(f"search_policy retrieved {len(chunks)} chunks in {latency_ms:.0f}ms")
            return [
                {
                    "doc_id": c["doc_id"],
                    "section": c["section"],
                    "excerpt": c["text"][:400],
                }
                for c in chunks
            ]

        if name == "get_next_slot":
            slot = get_next_slot(args["business_days_from_now"])
            return {"slot": slot.isoformat()}

        log.warning(f"unknown tool: {name}")
        return {"error": f"Unknown tool: {name}"}

    def _extract_plan(self, app_id: str, messages: list, log) -> AgentPlan:
        # Ask the model to produce the final structured JSON plan
        extraction_messages = messages + [
            {
                "role": "user",
                "content": (
                    "Based on your investigation, output your final plan now as a JSON object "
                    "with exactly these keys: ApplicationId, AgentStatus, AgentReasoning, PlanText."
                ),
            }
        ]
        try:
            result = self.client.beta.chat.completions.parse(
                model=self.config.model,
                messages=extraction_messages,
                response_format=AgentPlan,
            )
            plan = result.choices[0].message.parsed
            log.info(f"plan extracted: status={plan.AgentStatus}")
            return plan
        except Exception as exc:
            log.error(f"plan extraction failed: {exc}")
            return AgentPlan(
                ApplicationId=app_id,
                AgentStatus="requires human intervention",
                AgentReasoning=f"Structured plan extraction failed: {exc}",
                PlanText="Unable to produce a structured plan. Escalate to a senior operator.",
            )
