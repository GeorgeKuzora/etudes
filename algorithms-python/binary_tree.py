from queue import Queue
from random import randint
from dataclasses import dataclass
from typing import Self


@dataclass
class TreeNode:
    value: int
    left: Self | None
    right: Self | None
    parent: Self | None
    height: int


class Tree:
    def __init__(self, root: TreeNode | None) -> None:
        self.root: TreeNode | None = root

    def traverse_pre_order(self) -> list[int]:
        path: list[int] = []
        return self._pre_order_traversal(self.root, path)

    def traverse_in_order(self) -> list[int]:
        path: list[int] = []
        return self._in_order_traversal(self.root, path)

    def traverse_post_order(self) -> list[int]:
        path: list[int] = []
        return self._post_order_traversal(self.root, path)

    def _pre_order_traversal(self, curr: TreeNode | None, path: list[int]) -> list[int]:
        if curr is None:
            return path
        # pre
        path.append(curr.value)
        # recurse
        self._pre_order_traversal(curr.left, path)
        self._pre_order_traversal(curr.right, path)
        # post
        return path

    def _in_order_traversal(self, curr: TreeNode | None, path: list[int]) -> list[int]:
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
        self, curr: TreeNode | None, path: list[int]
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
        tree_queue: Queue[TreeNode | None] = Queue()
        tree_queue.put(self.root)
        while not tree_queue.empty():
            curr: TreeNode | None = tree_queue.get()
            if curr:
                path.append(curr.value)
            if curr and curr.left:
                tree_queue.put(curr.left)
            if curr and curr.right:
                tree_queue.put(curr.right)
        return path

    @classmethod
    def binary_tree(
        cls, number_of_nodes: int, min_value: int = 0, max_value: int = 100
    ) -> Self:
        root_node = TreeNode(randint(min_value, max_value), None, None, None, 1)
        tree: Self = cls(root_node)
        for _ in range(number_of_nodes - 1):
            tree.insert(randint(min_value, max_value))
        return tree

    def compare(self, tree_b: Self) -> bool:
        return self._compare(self.root, tree_b.root)

    @staticmethod
    def _compare(tree_node_a: TreeNode | None, tree_node_b: TreeNode | None) -> bool:
        if tree_node_a is None and tree_node_b is None:
            return True
        if tree_node_a is None or tree_node_b is None:
            return False
        if tree_node_a.value != tree_node_b.value:
            return False
        return Tree._compare(tree_node_a.left, tree_node_b.left) and Tree._compare(
            tree_node_a.right, tree_node_b.right
        )

    def find(self, value: int) -> bool:
        if self._find_in_binary_tree(self.root, value):
            return True
        return False

    def _find_in_binary_tree(
        self, current_node: TreeNode | None, value: int
    ) -> TreeNode | None:
        if current_node is None:
            return current_node
        if current_node.value == value:
            return current_node
        if current_node.value < value:
            return self._find_in_binary_tree(current_node.right, value)
        return self._find_in_binary_tree(current_node.left, value)

    def insert(self, value: int) -> bool:
        return self._insert_in_binary_tree(self.root, value)

    def _insert_in_binary_tree(
        self,
        current_node: TreeNode | None,
        value: int,
        parent_node: TreeNode | None = None,
        height: int = 1,
    ) -> bool:
        if current_node is None:
            return False
        parent_node = current_node
        if current_node.value >= value:
            if current_node.left:
                return self._insert_in_binary_tree(
                    current_node.left, value, parent_node, height + 1
                )
            current_node.left = TreeNode(value, None, None, parent_node, height)
            return True
        elif current_node.value < value:
            if current_node.right:
                return self._insert_in_binary_tree(
                    current_node.right, value, parent_node, height + 1
                )
            current_node.right = TreeNode(value, None, None, parent_node, height)
            return True
        return False

    def delete(self, value: int) -> bool:
        deleted_node: TreeNode | None = self._find_in_binary_tree(self.root, value)
        if deleted_node is None:
            return False
        if deleted_node.parent is None:
            if not deleted_node.right and not deleted_node.left:
                self.root = None
                return True
            if not deleted_node.left and deleted_node.right:
                deleted_node.right.parent = None
                self.root = deleted_node.right
                return True
            if not deleted_node.right and deleted_node.left:
                deleted_node.left.parent = None
                self.root = deleted_node.left
                return True
            if deleted_node.right and deleted_node.left:
                sub_tree_root_node = deleted_node.right
                smalest_node_in_sub_tree = sub_tree_root_node
                while smalest_node_in_sub_tree.left:
                    smalest_node_in_sub_tree = smalest_node_in_sub_tree.left
                smalest_node_in_sub_tree.left = deleted_node.left
                deleted_node.left.parent = smalest_node_in_sub_tree
                deleted_node.right.parent = None
                self.root = deleted_node.right
                return True
        on_the_left = deleted_node.value <= deleted_node.parent.value
        if deleted_node.left is None and deleted_node.right is None:
            if on_the_left:
                deleted_node.parent.left = None
            else:
                deleted_node.parent.right = None
            return True
        if deleted_node.left is None and deleted_node.right is not None:
            if on_the_left:
                deleted_node.parent.left = deleted_node.right
                deleted_node.right.parent = deleted_node.parent
            else:
                deleted_node.parent.right = deleted_node.right
                deleted_node.right.parent = deleted_node.parent
            return True
        if deleted_node.left is not None and deleted_node.right is None:
            if on_the_left:
                deleted_node.parent.left = deleted_node.left
                deleted_node.left.parent = deleted_node.parent
            else:
                deleted_node.parent.right = deleted_node.left
                deleted_node.left.parent = deleted_node.parent
            return True
        if deleted_node.left is not None and deleted_node.right is not None:
            sub_tree_root_node = deleted_node.left
            largest_node_in_sub_tree = sub_tree_root_node
            while largest_node_in_sub_tree.right:
                largest_node_in_sub_tree = largest_node_in_sub_tree.right
            largest_node_in_sub_tree.right = deleted_node.right
            if largest_node_in_sub_tree.left:
                sub_tree_root_node.parent = largest_node_in_sub_tree.left
                largest_node_in_sub_tree.left.left = sub_tree_root_node
            else:
                sub_tree_root_node.parent = largest_node_in_sub_tree
                largest_node_in_sub_tree.left = sub_tree_root_node
            if on_the_left:
                deleted_node.parent.left = largest_node_in_sub_tree
                largest_node_in_sub_tree.parent = deleted_node.parent
            else:
                deleted_node.parent.right = largest_node_in_sub_tree
                largest_node_in_sub_tree.parent = deleted_node.parent
            return True
        return False


if __name__ == "__main__":
    # tree = Tree.binary_tree(7)
    # pre_order_path: list[int] = tree.traverse_pre_order()
    # in_order_path: list[int] = tree.traverse_in_order()
    # post_order_path: list[int] = tree.traverse_post_order()
    # breadth_first_path: list[int] = tree.traverse_breadth_first()
    # print("PRE-ORDER")
    # print(pre_order_path)
    # print("IN-ORDER")
    # print(in_order_path)
    # print("POST-ORDER")
    # print(post_order_path)
    # print("BREADTH-FIRST-ORDER")
    # print(breadth_first_path)
    # tree_a = Tree.binary_tree(7)
    # tree_b = Tree.binary_tree(9)
    # print(tree_a.compare(tree_a))
    # print(tree_a.compare(tree_b))
    root = TreeNode(50, None, None, None, 1)
    binary_tree = Tree(root)
    # binary_tree_sorted_array: list[int] = binary_tree.traverse_in_order()
    # print(binary_tree_sorted_array)
    # for i in (10, 20, 30, 40, 50, 60, 70, 80, 90):
    #     if binary_tree.find(i):
    #         print(f"{i} true")
    values = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
    binary_tree.insert(60)
    binary_tree.insert(70)
    binary_tree.insert(80)
    binary_tree.insert(90)
    binary_tree.insert(100)
    binary_tree.insert(40)
    binary_tree.insert(30)
    binary_tree.insert(20)
    binary_tree.insert(10)
    binary_tree.insert(0)
    print(binary_tree.traverse_in_order())
    binary_tree.delete(values[randint(0, 10)])
    print(binary_tree.traverse_in_order())
