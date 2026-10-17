import json
import random
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from fixtures import FixtureStore, ToolProxy
from adapter import run_langgraph_agent
from checks import run_all_checks


def real_lookup_order(order_id):
    if order_id == "A1":
        return "shipped"
    return "processing"


# Record the tool answers once (real tool is called here)
store = FixtureStore()
recorder = ToolProxy("lookup_order", real_lookup_order, store, "record")
recorder.call(order_id="A1")
recorder.call(order_id="B2")

# From now on, the agent can only replay
tool = ToolProxy("lookup_order", real_lookup_order, store, "replay")

flaky_dice = random.Random(3)


class AgentState(TypedDict):
    question: str
    order_id: str
    status: str
    answer: str


def find_order(state):
    order_id = state["question"].split()[-1]
    status = tool.call(order_id=order_id)
    return {"order_id": order_id, "status": status}


def write_answer(state):
    # A flaky step: 25% of the time the agent forgets the JSON format
    if flaky_dice.random() < 0.25:
        return {"answer": "Your order is " + state["status"]}
    answer = {"status": state["status"], "message": "Order " + state["order_id"] + " is " + state["status"]}
    return {"answer": json.dumps(answer)}


builder = StateGraph(AgentState)
builder.add_node("find_order", find_order)
builder.add_node("write_answer", write_answer)
builder.add_edge(START, "find_order")
builder.add_edge("find_order", "write_answer")
builder.add_edge("write_answer", END)
graph = builder.compile()

rules = {
    "required_tool": "lookup_order",
    "required_keys": ["status", "message"],
    "max_steps": 5,
}

print("Running the LangGraph agent 10 times on: Where is order A1")
for run_number in range(1, 11):
    result = run_langgraph_agent(graph, "Where is order A1", store)
    passed, failures = run_all_checks(result, rules)
    print("run", run_number, "| steps:", result.steps, "| tools:", result.tools_called,
          "|", "PASS" if passed else "FAIL")
    if not passed:
        print("      output was:", result.output)

print()
print("Now a question about an order we never recorded:")
try:
    run_langgraph_agent(graph, "Where is order Z9", store)
except Exception as problem:
    print("  Error:", type(problem).__name__)