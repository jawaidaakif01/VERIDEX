from triage_eval import DEFAULT_CLASSIFY_PROMPT, DEFAULT_DRAFT_PROMPT, DEFAULT_CHECK_PROMPT

FIXED_DRAFT_PROMPT = """Write a short professional support response to this {category} ticket: {ticket_text}
Do not use placeholders in square brackets. Sign the response as 'Support Team'."""

REWORDED_CLASSIFY_PROMPT = """Read the support ticket below. Decide its category (billing, technical, or general) and its priority (high or low).
    Ticket: {ticket_text}
    Reply exactly in this format: category=<x>, priority=<y>
    """

STRICT_PRIORITY_CLASSIFY_PROMPT = """Classify this support ticket into exactly one category:
    billing, technical, or general. Also rate priority as high or low.
    Use high only if the customer cannot use the product at all or is losing money right now. Otherwise use low.
    Ticket: {ticket_text}
    Respond in format: category=<x>, priority=<y>
    """

VERSIONS = [
    {"name": "v0_baseline", "draft_prompt": FIXED_DRAFT_PROMPT},
    {"name": "v1_aa_rerun", "draft_prompt": FIXED_DRAFT_PROMPT},
    {"name": "v2_reworded", "draft_prompt": FIXED_DRAFT_PROMPT,
     "classify_prompt": REWORDED_CLASSIFY_PROMPT},
    {"name": "v3_placeholder_bug", "draft_prompt": DEFAULT_DRAFT_PROMPT},
    {"name": "v4_strict_priority", "draft_prompt": FIXED_DRAFT_PROMPT,
     "classify_prompt": STRICT_PRIORITY_CLASSIFY_PROMPT},
]