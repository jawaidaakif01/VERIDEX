from triage_run import run_triage_version

FIXED_DRAFT_PROMPT = """Write a short professional support response to this {category} ticket: {ticket_text}
Do not use placeholders in square brackets. Sign the response as 'Support Team'."""

run_triage_version("baseline_fixed", n_runs=5, draft_prompt=FIXED_DRAFT_PROMPT)