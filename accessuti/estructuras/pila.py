class Pila:
    def __init__(self):
        self.data = []

    def push(self, x):
        self.data.append(x)

    def pop(self):
        return self.data.pop() if self.data else None

    def to_list(self):
        return self.data[::-1]