import os
from fixtures import FixtureStore, ToolProxy, FixtureMismatchError


def real_lookup_order(order_id):
    print("   (real tool was called for", order_id + ")")
    if order_id == "A1":
        return "shipped"
    return "processing"


def broken_real_tool(order_id):
    raise RuntimeError("The real tool must NOT be called during replay!")


os.makedirs("results", exist_ok=True)

print("STEP 1: RECORD mode (real tool is called)")
store = FixtureStore()
recorder = ToolProxy("lookup_order", real_lookup_order, store, "record")
print("  A1 ->", recorder.call(order_id="A1"))
print("  B2 ->", recorder.call(order_id="B2"))
store.save("results/fixtures.json")
print("  Saved", len(store.saved_answers), "tool answers")
print()

print("STEP 2: REPLAY mode (real tool is never called)")
new_store = FixtureStore()
new_store.load("results/fixtures.json")
replayer = ToolProxy("lookup_order", broken_real_tool, new_store, "replay")
print("  A1 ->", replayer.call(order_id="A1"))
print("  B2 ->", replayer.call(order_id="B2"))
print()

print("STEP 3: the new agent asks for something we never recorded")
try:
    replayer.call(order_id="Z9")
except FixtureMismatchError as problem:
    print("  Caught the mismatch error:")
    print("  ", problem)