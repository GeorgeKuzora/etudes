from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Node:
    value: Any
    prev: Self | None
    next: Self | None


class LRU:
    def __init__(self, capacity: int) -> None:
        self.length: int = 0
        self.capacity: int = capacity
        self.head: Node | None = None
        self.tail: Node | None = None
        self.lookup: dict[Any, Node | None] = {}
        self.reverse_lookup: dict[Node | None, Any] = {}

    def update(self, key: Any, value: Any) -> None:
        node: Node | None = self.lookup.get(key)
        if not node:
            node = Node(value, None, None)
            self.length += 1
            self.prepend(node)
            self.trim_cache()
            self.lookup[key] = node
            self.reverse_lookup[node] = key
        else:
            self.detach(node)
            self.prepend(node)
            node.value = value

    def get(self, key: Any) -> Any | None:
        # check cache for existence
        node: Node | None = self.lookup.get(key)
        if not node:
            return None
        # update value we found and move to the front
        self.detach(node)
        self.prepend(node)
        # return node value
        return node.value

    def detach(self, node: Node | None) -> None:
        if not node:
            return
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if self.head == node and self.head:
            self.head = self.head.next
        if self.tail == node and self.tail:
            self.tail = self.tail.prev

        node.next = None
        node.prev = None

    def prepend(self, node: Node) -> None:
        if not self.head:
            self.head = self.tail = node
            return
        node.next = self.head
        self.head.prev = node
        self.head = node

    def trim_cache(self) -> None:
        if self.length <= self.capacity:
            return
        tail = self.tail
        self.detach(self.tail)

        key = self.reverse_lookup.pop(tail)
        self.lookup.pop(key)
        self.length -= 1
