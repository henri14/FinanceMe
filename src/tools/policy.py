"""Mock policy lookup. Returns policy text snippets keyed by topic.

In a production system this would be a thin wrapper over the Mission 2
RAG service. Here it's a static dict so Mission 3 can be solved
independently of Mission 2.
"""

from __future__ import annotations


_POLICIES: dict[str, str] = {
    "verification_sla": (
        "Per the Acme Operations SLA Handbook (AC-HANDBO), section 2, "
        "the verification SLA is 3 business days, measured from the time "
        "all requested customer documents have been received. Per section 3, "
        "an application is automatically escalated for manual review by an "
        "Operations Lead on day 5 of verification."
    ),
    "contact_preferences": (
        "Per the Acme Personal Lending Policy (AC-POLICY), section 5, "
        "the default contact-channel priority when Acme initiates contact "
        "is: (1) SMS, (2) email 24 hours after SMS, (3) voice call only "
        "after SMS and email are unanswered, unless the customer has "
        "explicitly opted in to phone contact. Customer-declared preferences "
        "override the default order."
    ),
    "hardship_escalation": (
        "Per the Acme Financial Hardship Policy (AC-POLICY), section 4, "
        "escalation on a non-responsive hardship file proceeds as: day 1 "
        "acknowledgement; day 3 reminder via preferred channel; day 7 "
        "second reminder offering a different channel; day 14 supervisor "
        "review; day 21 file closed as 'unable to assess' and standard "
        "collections resumes."
    ),
    "business_hours": (
        "Per the Acme Operations SLA Handbook (AC-HANDBO), section 1, "
        "business hours are 08:00–18:00 AEST, Monday to Friday, excluding "
        "NSW public holidays. No outbound customer contact is initiated "
        "outside of business hours."
    ),
    "cooling_off": (
        "Per the Acme Personal Lending Policy (AC-POLICY), section 4.1, "
        "approved applicants are entitled to a cooling-off period of 14 "
        "business days from contract signing, during which the contract "
        "may be cancelled at no cost."
    ),
    "fees": (
        "Per the Acme Product Information (AC-INFO), section 2: "
        "establishment fee $499 at settlement; monthly account fee $10 in "
        "arrears; dishonour fee $15; no early repayment fee for "
        "variable-rate products."
    ),
}


def get_policy(topic: str) -> str:
    """Return policy text for a given topic.

    Returns an empty string if the topic is unknown — agents should treat
    an empty result as 'no policy available for that topic'.

    Known topics: verification_sla, contact_preferences, hardship_escalation,
    business_hours, cooling_off, fees.
    """
    return _POLICIES.get(topic, "")
