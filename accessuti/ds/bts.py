class BSTNode:
    __slots__ = ("key", "data", "left", "right")

    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.left = None
        self.right = None


class BST:
    """
    BST por key (string). Útil para:
      - buscar usuario por username en O(h)
      - listar ordenado (inorder)
    """

    def __init__(self):
        self.root = None

    def insert(self, key, data):
        key = str(key)

        if self.root is None:
            self.root = BSTNode(key, data)
            return

        cur = self.root
        while True:
            if key < cur.key:
                if cur.left is None:
                    cur.left = BSTNode(key, data)
                    return
                cur = cur.left
            elif key > cur.key:
                if cur.right is None:
                    cur.right = BSTNode(key, data)
                    return
                cur = cur.right
            else:
                # UPDATE si ya existe
                cur.data = data
                return

    def search(self, key):
        key = str(key)
        cur = self.root
        while cur:
            if key < cur.key:
                cur = cur.left
            elif key > cur.key:
                cur = cur.right
            else:
                return cur.data
        return None

    def inorder(self):
        out = []

        def _walk(node):
            if not node:
                return
            _walk(node.left)
            out.append(node.data)
            _walk(node.right)

        _walk(self.root)
        return out