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


if __name__ == "__main__":
    app()
