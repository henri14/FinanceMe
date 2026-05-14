# Simple LLM Chat Client

Build a Python chat client with full cost and latency telemetry. Think of it as flying the plane with every gauge visible.
The chat client should:
- use OpenAI API for the LLM
- The model should be configurable, with a default of gpt-5.4-nano
- Be compatible with Python 3.11
- Responses from the LLM should be streamed
- Collect the following metrics for the client
  - Number of tokens in the prompt
  - Number of tokens in the chat completion
  - Cost in USD
  - Latency in ms
- Emit metrics in two formats
  - As a line of text
  - As a JSON stream to a file

This project will be extended in the future, keep the folder structure modular.

Produce a plan for implementing an LLM chat client as per the attached instructions. Recommend a set of frameworks or libraries to do this. Keep in mind that I would like to implement features like a persistent store for chat interactions; retrieval augmented generation; tool calling; evaluation.
