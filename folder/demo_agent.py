import json
import random
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from fixtures import FixtureStore, ToolProxy


class AgentState(TypedDict):
    question: str
    order_id: str
    status: str
    answer: str


def real_lookup_order(order_id):
    if order_id == "A1":
        return "shipped"
    if order_id == "B2":
        return "processing"
    if order_id == "C3":
        return "delivered"
    return "cancelled"


def make_store():
    store = FixtureStore()
    recorder = ToolProxy("lookup_order", real_lookup_order, store, "record")
    for order_id in ["A1", "B2", "C3", "D4"]:
        recorder.call(order_id=order_id)
    return store


def build_graph(store, flaky_chance, seed):
    tool = ToolProxy("lookup_order", real_lookup_order, store, "replay")
    dice = random.Random(seed)

    def find_order(state):
        order_id = state["question"].split()[-1]
        status = tool.call(order_id=order_id)
        return {"order_id": order_id, "status": status}

    def write_answer(state):
        if dice.random() < flaky_chance:
            return {"answer": "Your order is " + state["status"]}
        answer = {"status": state["status"], "message": "Order " + state["order_id"] + " is " + state["status"]}
        return {"answer": json.dumps(answer)}

    builder = StateGraph(AgentState)
    builder.add_node("find_order", find_order)
    builder.add_node("write_answer", write_answer)
    builder.add_edge(START, "find_order")
    builder.add_edge("find_order", "write_answer")
    builder.add_edge("write_answer", END)
    return builder.compile()