class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = TreeNode(value)
            return
        current = self.root
        while True:
            if value < current.value:
                if current.left is None:
                    current.left = TreeNode(value)
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = TreeNode(value)
                    return
                current = current.right

    def search(self, value):
        return self._search_from(value, self.root)

    def _search_from(self, value, node):
        if node is None:
            return False
        if value == node.value:
            return True
        elif value < node.value:
            return self._search_from(value, node.left)
        else:
            return self._search_from(value, node.right)

    # insert/search are O(log n) on average because each comparison
    # eliminates one whole subtree (left or right) instead of checking
    # every node — but this only holds if the tree stays roughly
    # balanced. If values are inserted in sorted order, the tree
    # degrades into a straight line and becomes O(n), same as a
    # linked list.
    def in_order(self, node="start", result=None):
        if result is None:
            result = []
        if node == "start":
            node = self.root
        if node is not None:
            self.in_order(node.left, result)
            result.append(node.value)
            self.in_order(node.right, result)
        return result


# Demo: build BST from non-sorted values
bst = BST()
for value in [50, 30, 70, 20, 40, 60, 80]:
    bst.insert(value)

print("Search 40:", bst.search(40))
print("Search 99:", bst.search(99))
print("In-order (sorted):", bst.in_order())