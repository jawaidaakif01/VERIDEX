from dotenv import load_dotenv
from langchain_groq import ChatGroq
from triage_eval import build_triage_graph

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
graph = build_triage_graph(llm)

tickets = [
    "I was charged twice for my subscription this month, please fix urgently!",
    "The app crashes every time I open the settings page.",
    "Do you offer a discount for students?",
]

for ticket in tickets:
    state = graph.invoke({
        "ticket_text": ticket,
        "category": "",
        "priority": "",
        "draft_response": "",
        "revision_count": 0,
        "approved": False,
    })
    print("TICKET:", ticket)
    print("   category:", state["category"], "| priority:", state["priority"])
    print("   revisions:", state["revision_count"], "| approved:", state["approved"])
    print("   draft:", state["draft_response"][:80])
    print()