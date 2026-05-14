# The Vault - RAG Service

Add a retrieval augmented generation service to the project. The chat client should make use of the knowledge base incorporated in this RAG service.

The RAG service should have the following attributes:
- Expose a /ask endpoint that returns an answer with inline citations pointing back to source chunks
- Expose a /metrics endpoint to provide Prometheus style metrics
    - Include metrics on retrieval latency, input and response sizes
- Frameworks / libraries
    - Use FastAPI as the framework
    - Use LanceDB as the vector database
    - Use DeepEval for evaluation of the RAG service
- Provide a tool to load the vector database with the knowledge base or corpus. The corpus is provided as markdown files in the `corpus` folder.
- Target performance to be less than 300ms
- Generate a set of 10 questions for evaluation of the RAG service.