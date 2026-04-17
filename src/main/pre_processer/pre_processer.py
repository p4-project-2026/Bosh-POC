class PreProcesser:
    def __init__(self, data):
        self.data = data

    def run(self):
        self.whitespace_strip()
        self.insert_symbols_at_nested_indents()

    def whitespace_strip(self):
        self.data = self.data.strip()

    def insert_symbols_at_nested_indents(self):
        # inserts {} around nested blocks of indented code
        indent_level = 0
        indent_level_stack = [0] 
        data = self.data.splitlines()
        for i, line in enumerate(data):
            indent_level = len(line) - len(line.lstrip())
            if (line.strip() == ""): continue
            if (indent_level == indent_level_stack[-1]): continue

            if indent_level > indent_level_stack[-1]:
                data[i-1] += " {"
                indent_level_stack.append(indent_level)
            else:
                while indent_level < indent_level_stack[-1]:
                    data[i-1] += "}"
                    indent_level_stack.pop()

        self.data = "\n".join(data)

