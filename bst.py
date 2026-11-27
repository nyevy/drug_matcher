# unbalanced binary search tree with subtree size fields for order statistics
# includes insert, delete, search, predecessor, rank, select, and tree rotations


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.size = 1


def size(node):
    return node.size if node else 0


def update(node):
    node.size = 1 + size(node.left) + size(node.right)


def insert(node, key, value):
    if node is None:
        return Node(key, value)
    if key < node.key:
        node.left = insert(node.left, key, value)
    elif key > node.key:
        node.right = insert(node.right, key, value)
    else:
        node.value = value   # same key, overwrite
    update(node)
    return node


def search(node, key):
    while node is not None:
        if key == node.key:
            return node
        node = node.left if key < node.key else node.right
    return None


def _min_node(node):
    while node.left is not None:
        node = node.left
    return node


def delete(node, key):
    if node is None:
        return None
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        node.right = delete(node.right, key)
    else:
        # 0 or 1 child: just splice the node out
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        # 2 children: copy the successor (min of right subtree) up, then delete it
        succ = _min_node(node.right)
        node.key, node.value = succ.key, succ.value
        node.right = delete(node.right, succ.key)
    update(node)
    return node


def in_order(node, out=None):
    # left, node, right gives sorted order
    if out is None:
        out = []
    if node is not None:
        in_order(node.left, out)
        out.append((node.key, node.value))
        in_order(node.right, out)
    return out


def predecessor(node, key):
    # biggest key that is strictly smaller than key
    best = None
    while node is not None:
        if node.key < key:
            best = node
            node = node.right
        else:
            node = node.left
    return best


def select(node, k):
    # k-th smallest, k starts at 1
    while node is not None:
        left_size = size(node.left)
        if k == left_size + 1:
            return node
        if k <= left_size:
            node = node.left
        else:
            k -= left_size + 1
            node = node.right
    return None


def rank(node, key):
    # how many keys are smaller than key
    r = 0
    while node is not None:
        if key <= node.key:
            node = node.left
        else:
            r += size(node.left) + 1
            node = node.right
    return r


def rotate_left(node):
    # right child moves up
    child = node.right
    node.right = child.left
    child.left = node
    update(node)
    update(child)
    return child


def rotate_right(node):
    # left child moves up
    child = node.left
    node.left = child.right
    child.right = node
    update(node)
    update(child)
    return child


def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))
