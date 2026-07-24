from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Any, Self

Color = Enum("Color", ["RED", "BLACK"])


@dataclass
class Node:
    value: Any
    parent: Self | None
    left: Self | None
    right: Self | None
    color: Color





class RedBlackTree:
    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, value: Any) -> None:
        node: Node = Node(value, None, None, None, Color.RED)
        self._insert_node(node, self.root)
        self.insert_fixup(node)

    def _insert_node(self, node: Node, parent: Node | None) -> None:
        if node is None:
            return
        if parent is None:
            self.root = node
            return
        if parent.left is None and node.value <= parent.value:
            parent.left = node
            node.parent = parent
            return
        if parent.right is None and node.value > parent.value:
            parent.right = node
            node.parent = parent
            return
        if node.value <= parent.value:
            self._insert_node(node, parent.left)
        if node.value > parent.value:
            self._insert_node(node, parent.right)

    def insert_fixup(self, node: Node) -> None:
        ll: bool = False
        rr: bool = False
        lr: bool = False
        rl: bool = False
        recolor: bool = False

        red_red_conflict = False
        # base case we are on the root of the tree
        if node is self.root or not node.parent:
            node.color = Color.BLACK
            return

        # check if we have conflict
        if node.color == Color.RED and node.parent.color == Color.RED:
            red_red_conflict = True

        if red_red_conflict:
            # check if parent and uncle has similar color
            recolor = self.is_recolor(node)
            if not recolor:
                ll = self.is_left_left(node)
                rr = self.is_right_right(node)
                lr = self.is_left_right(node)
                rl = self.is_right_left(node)
            if recolor:
                node = self.recolor(node.parent)
            if ll:
                node = self.rotate_left(node.parent.parent)
                node.color = Color.BLACK
                node.left.color = Color.RED
            if rr:
                node = self.rotate_right(node.parent.parent)
                node.color = Color.BLACK
                node.right.color = Color.RED
            if rl:
                node = self.rotate_right(node.parent)
                node = self.rotate_left(node.parent)
                node.color = Color.BLACK
                node.left.color = Color.RED
            if lr:
                node = self.rotate_left(node.parent)
                node = self.rotate_right(node.parent)
                node.color = Color.BLACK
                node.right.color = Color.RED
            return (self.insert_fixup(node))

    def is_recolor(self, node: Node) -> bool:
        first_parent_sibling = None
        second_parent_sibling = None
        if node.parent and node.parent.parent:
            first_parent_sibling = node.parent.parent.left
            second_parent_sibling = node.parent.parent.right
        if (first_parent_sibling and first_parent_sibling.color == Color.RED) and (
            second_parent_sibling and second_parent_sibling.color == Color.RED
        ):
            return True
        return False

    def is_left_left(self, node: Node) -> bool:
        parent = node.parent
        grand_parent = None
        if parent:
            grand_parent = parent.parent
        if (
            grand_parent
            and parent
            and parent is grand_parent.left
            and node is parent.left
        ):
            return True
        return False

    def is_left_right(self, node: Node) -> bool:
        parent = node.parent
        grand_parent = None
        if parent:
            grand_parent = parent.parent
        if (
            grand_parent
            and parent
            and parent is grand_parent.left
            and node is parent.right
        ):
            return True
        return False

    def is_right_right(self, node: Node) -> bool:
        parent = node.parent
        grand_parent = None
        if parent:
            grand_parent = parent.parent
        if (
            grand_parent
            and parent
            and parent is grand_parent.right
            and node is parent.left
        ):
            return True
        return False

    def is_right_left(self, node: Node) -> bool:
        parent = node.parent
        grand_parent = None
        if parent:
            grand_parent = parent.parent
        if (
            grand_parent
            and parent
            and parent is grand_parent.right
            and node is parent.right
        ):
            return True
        return False

    def rotate_left(self, node: Node) -> Node:
        node_right_child = node.right
        if not node_right_child:
            return node
        child_left_child = node_right_child.left
        node_right_child.left = node
        node_right_child.parent = node.parent
        node.parent = node_right_child
        node.right = child_left_child
        if child_left_child:
            child_left_child.parent = node
        return node_right_child

    def rotate_right(self, node: Node) -> Node:
        node_left_child = node.left
        if not node_left_child:
            return node
        child_right_child = node_left_child.right
        node_left_child.right = node
        node_left_child.parent = node.parent
        node.parent = node_left_child
        node.left = child_right_child
        if child_right_child:
            child_right_child.parent = node
        return node_left_child

    def delete(self) -> Any:
        pass

    def recolor(self, node: Node) -> Node | None:
        if node.parent and node.parent.left and node.parent.right:
            node.parent.left.color = Color.BLACK
            node.parent.right.color = Color.BLACK
            node.parent.color = Color.RED
        return node.parent

    def traverse_pre_order(self) -> list[int]:
        path: list[int] = []
        return self._pre_order_traversal(self.root, path)

    def traverse_in_order(self) -> list[int]:
        path: list[int] = []
        return self._in_order_traversal(self.root, path)

    def traverse_post_order(self) -> list[int]:
        path: list[int] = []
        return self._post_order_traversal(self.root, path)

    def _pre_order_traversal(self, curr: Node | None, path: list[int]) -> list[int]:
        if curr is None:
            return path
        # pre
        path.append(curr.value)
        # recurse
        self._pre_order_traversal(curr.left, path)
        self._pre_order_traversal(curr.right, path)
        # post
        return path

    def _in_order_traversal(self, curr: Node | None, path: list[int]) -> list[int]:
        if curr is None:
            return path
        # pre
        # recurse
        self._in_order_traversal(curr.left, path)
        path.append(curr.value)
        self._in_order_traversal(curr.right, path)
        # post
        return path

    def _post_order_traversal(
        self, curr: Node | None, path: list[int]
    ) -> list[int]:
        if curr is None:
            return path
        # pre
        # recurse
        self._post_order_traversal(curr.left, path)
        self._post_order_traversal(curr.right, path)
        # post
        path.append(curr.value)
        return path

    def traverse_breadth_first(self) -> list[int]:
        path: list[int] = []
        tree_queue: Queue[Node | None] = Queue()
        tree_queue.put(self.root)
        while not tree_queue.empty():
            curr: Node | None = tree_queue.get()
            if curr:
                path.append(curr.value)
            if curr and curr.left:
                tree_queue.put(curr.left)
            if curr and curr.right:
                tree_queue.put(curr.right)
        return path


if __name__ == "__main__":
    tree = RedBlackTree()
    tree.insert(6)
    tree.insert(1)
    tree.insert(9)
    tree.insert(7)
    tree.insert(2)
    tree.insert(3)
    tree.insert(4)
    tree.insert(8)
    tree.insert(5)
    print(tree.traverse_in_order())
