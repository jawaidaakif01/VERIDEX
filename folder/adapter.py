import json
from models import AgentResult


def run_langgraph_agent(graph, question, store=None, input_key="question",
                        output_key="answer", output_keys=None):
    if store is not None:
        store.call_log = []
    steps = 0
    final_state = {}
    for update in graph.stream({input_key: question}, stream_mode="updates"):
        for node_name, node_output in update.items():
            steps = steps + 1
            if node_output:
                final_state.update(node_output)

    if output_keys is not None:
        data = {}
        for key in output_keys:
            data[key] = final_state.get(key)
        output_text = json.dumps(data)
    else:
        output_text = str(final_state.get(output_key, ""))

    tools_called = []
    if store is not None:
        tools_called = list(store.call_log)

    result = AgentResult(
        output=output_text,
        tools_called=tools_called,
        steps=steps,
    )
    return result