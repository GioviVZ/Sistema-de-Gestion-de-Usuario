class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if not self._data:
            return None
        return self._data.pop()

    def peek(self):
        if not self._data:
            return None
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def to_list(self):
        # devuelve de más reciente a más antiguo
        return list(reversed(self._data))