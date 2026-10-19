from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

DEFAULT_CLASSIFY_PROMPT = """Classify this support ticket into exactly one category:
    billing, technical, or general. Also rate priority as high or low.
    Ticket: {ticket_text}
    Respond in format: category=<x>, priority=<y>
    """

DEFAULT_DRAFT_PROMPT = """Write a short professional support response to this {category} ticket: {ticket_text}"""

DEFAULT_CHECK_PROMPT = """Is this response professional, on-topic, and helpful? Answer only YES or NO.
    Response: {draft_response}
    """


class TicketState(TypedDict):
    ticket_text: str
    category: str
    priority: str
    draft_response: str
    revision_count: int
    approved: bool


def build_triage_graph(llm,
                       classify_prompt=DEFAULT_CLASSIFY_PROMPT,
                       draft_prompt=DEFAULT_DRAFT_PROMPT,
                       check_prompt=DEFAULT_CHECK_PROMPT):

    def classify_ticket(state: TicketState) -> dict:
        prompt = classify_prompt.format(ticket_text=state["ticket_text"])
        response = llm.invoke(prompt).text

        if "billing" in response.lower():
            category = "billing"
        elif "technical" in response.lower():
            category = "technical"
        else:
            category = "general"

        if "high" in response.lower():
            priority = "high"
        else:
            priority = "low"

        return {"category": category, "priority": priority}

    def draft_response(state: TicketState) -> dict:
        prompt = draft_prompt.format(category=state["category"], ticket_text=state["ticket_text"])
        draft = llm.invoke(prompt).text
        count = state.get("revision_count", 0) + 1
        return {"draft_response": draft, "revision_count": count}

    def check_quality(state: TicketState) -> dict:
        prompt = check_prompt.format(draft_response=state["draft_response"])
        verdict = llm.invoke(prompt).text.strip().upper()
        return {"approved": "YES" in verdict}

    def escalate(state: TicketState) -> dict:
        return {}

    def route_by_priority(state: TicketState) -> Literal["escalate", "draft_response"]:
        if state["priority"] == "high":
            return "escalate"
        return "draft_response"

    def route_by_quality(state: TicketState) -> Literal["draft_response", "end"]:
        if not state["approved"] and state["revision_count"] < 3:
            return "draft_response"
        return "end"

    graph = StateGraph(TicketState)
    graph.add_node("classify", classify_ticket)
    graph.add_node("escalate", escalate)
    graph.add_node("draft_response", draft_response)
    graph.add_node("check_quality", check_quality)

    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", route_by_priority, {
        "escalate": "escalate",
        "draft_response": "draft_response",
    })
    graph.add_edge("draft_response", "check_quality")
    graph.add_conditional_edges("check_quality", route_by_quality, {
        "draft_response": "draft_response",
        "end": END,
    })
    graph.add_edge("escalate", END)

    return graph.compile()