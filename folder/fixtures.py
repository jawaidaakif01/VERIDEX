import json


class FixtureMismatchError(Exception):
    pass


def make_key(tool_name, arguments):
    return tool_name + "|" + json.dumps(arguments, sort_keys=True)


class FixtureStore:
    def __init__(self):
        self.saved_answers = {}
        self.call_log = []

    def record(self, tool_name, arguments, result):
        key = make_key(tool_name, arguments)
        self.saved_answers[key] = result

    def lookup(self, tool_name, arguments):
        key = make_key(tool_name, arguments)
        if key not in self.saved_answers:
            raise FixtureMismatchError(
                "No recorded answer for tool '" + tool_name + "' with arguments "
                + json.dumps(arguments, sort_keys=True)
                + ". The agent asked for something we never recorded."
            )
        return self.saved_answers[key]

    def save(self, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.saved_answers, file, indent=2)

    def load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            self.saved_answers = json.load(file)


class ToolProxy:
    def __init__(self, tool_name, real_function, store, mode):
        self.tool_name = tool_name
        self.real_function = real_function
        self.store = store
        self.mode = mode

    def call(self, **arguments):
        self.store.call_log.append(self.tool_name)
        if self.mode == "record":
            result = self.real_function(**arguments)
            self.store.record(self.tool_name, arguments, result)
            return result
        if self.mode == "replay":
            return self.store.lookup(self.tool_name, arguments)
        raise ValueError("mode must be 'record' or 'replay'")