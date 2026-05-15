TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_application",
            "description": (
                "Look up a loan application by ID in the CRM system. "
                "Returns application status, days in current status, contact preferences, "
                "and masked customer identifiers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "The application ID, e.g. A-1423",
                    }
                },
                "required": ["app_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": (
                "Search the Acme FinanceMe policy and SLA knowledge base using natural language. "
                "Returns a synthesized answer with source citations. "
                "Use this to look up verification SLAs, hardship procedures, contact rules, "
                "fee schedules, regulatory requirements, and any other policy questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query about Acme policy, SLA, or regulation",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_slot",
            "description": (
                "Return the next available appointment slot a given number of business days "
                "from today (NSW business days, excluding public holidays). "
                "Use this to schedule follow-up calls or customer contact."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "business_days_from_now": {
                        "type": "integer",
                        "description": "Number of business days from today",
                    }
                },
                "required": ["business_days_from_now"],
            },
        },
    },
]
