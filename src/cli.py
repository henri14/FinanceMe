import asyncio
import sys
from pathlib import Path

import typer

# Ensure the repository root is on sys.path so `src` can be imported when running this file directly.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.client import ChatClient

app = typer.Typer()


@app.command()
def chat():
    """Start an interactive chat session."""
    client = ChatClient()
    asyncio.run(client.start_chat())


@app.command()
def copilot(
    app_id: str = typer.Argument(..., help="Application ID, e.g. A-1423"),
    question: str = typer.Argument(..., help="Question about the application"),
):
    """Run the Operations Copilot agent and print a structured action plan."""
    from src.extensions.tools.agent import CopilotAgent
    plan = CopilotAgent().run(app_id=app_id, question=question)
    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
