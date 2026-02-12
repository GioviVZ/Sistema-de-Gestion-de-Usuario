class NodoBST:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None

class ArbolUsuarios:
    def __init__(self):
        self.root = None

    def insertar(self, key, data):
        def _insert(node, key, data):
            if not node:
                return NodoBST(key, data)
            if key < node.key:
                node.left = _insert(node.left, key, data)
            elif key > node.key:
                node.right = _insert(node.right, key, data)
            return node
        self.root = _insert(self.root, key, data)

    def buscar(self, key):
        cur = self.root
        while cur:
            if key == cur.key:
                return cur.data
            cur = cur.left if key < cur.key else cur.right
        return None

    def inorder(self):
        res = []
        def _in(node):
            if node:
                _in(node.left)
                res.append(node.data)
                _in(node.right)
        _in(self.root)
        return res