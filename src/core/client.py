import time

from openai import OpenAI

from src.core.config import load_config
from src.core.metrics import MetricsCollector
from src.storage.db import Database


class ChatClient:
    def __init__(self):
        self.config = load_config()
        self.client = OpenAI(api_key=self.config.api_key)
        self.metrics = MetricsCollector()
        self.db = Database("data/chat_history.db")
        self.model = self.config.model
        self.max_turns = self.config.max_turns

    async def start_chat(self):
        print(f"Starting chat with model={self.model}")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"quit", "exit"}:
                print("Goodbye.")
                break
            self.db.save_message("user", user_input)

            last_turns = self.db.get_last_turns(self.max_turns)
            messages = [
                {"role": role, "content": content} for role, content in last_turns
            ]
            messages.append({"role": "user", "content": user_input})

            start = time.perf_counter()
            response = self.client.responses.create(
                model=self.model,
                input=messages,
            )
            latency = (time.perf_counter() - start) * 1000

            text = response.output_text.strip()
            usage = response.usage
            cost = self._estimate_cost(usage)

            print(f"Assistant: {text}")
            await self.metrics.collect(usage, cost, latency)
            self.db.save_message("assistant", text)

    def _estimate_cost(self, usage):
        # Rates for gpt-4o-mini ($/token). Update if model changes.
        prompt_rate = 0.00000015
        completion_rate = 0.00000060
        return (usage.input_tokens * prompt_rate) + (
            usage.output_tokens * completion_rate
        )
