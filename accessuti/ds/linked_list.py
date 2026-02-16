class LinkedList:
    def __init__(self):
        self._data = []

    def append(self, value):
        self._data.append(value)

    def to_list(self):
        return list(self._data)