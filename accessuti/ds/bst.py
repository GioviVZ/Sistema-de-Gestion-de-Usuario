class Node:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
        self.last_comparisons = 0

    def insert(self, key, data):
        self.last_comparisons = 0
        if not self.root:
            self.root = Node(key, data)
            return

        cur = self.root
        while True:
            self.last_comparisons += 1
            if key < cur.key:
                if not cur.left:
                    cur.left = Node(key, data)
                    return
                cur = cur.left
            elif key > cur.key:
                if not cur.right:
                    cur.right = Node(key, data)
                    return
                cur = cur.right
            else:
                cur.data = data
                return

    def search(self, key):
        self.last_comparisons = 0
        cur = self.root
        while cur:
            self.last_comparisons += 1
            if key < cur.key:
                cur = cur.left
            elif key > cur.key:
                cur = cur.right
            else:
                return cur.data
        return None