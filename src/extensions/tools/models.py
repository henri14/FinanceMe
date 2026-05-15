from typing import Literal

from pydantic import BaseModel


class AgentPlan(BaseModel):
    ApplicationId: str
    AgentStatus: Literal["plan generated", "requires human intervention"]
    AgentReasoning: str
    PlanText: str
