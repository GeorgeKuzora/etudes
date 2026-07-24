from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import logging

class Node:
    def __init__(self, value) -> None:
        self.value = value
        self.next = None
        self.previous = None

    def __str__(self) -> str:
        return f"{self.value}"


class LinkedList:
    def __init__(self) -> None:
        self.head = None
        self.tail = None
        self.length = 0

    def __str__(self) -> str:
        repr: str = ""
        current = self.head
        while current is not None:
            repr = f"{repr} <-> {current.value}"
            current = current.next
        return repr

    def prepend(self, node) -> None:
        self.length += 1
        if self.head is None:
            self.head = self.tail = node
            return
        node.next = self.head
        self.head.previous = node
        self.head = node

    def append(self, node) -> None:
        self.length += 1
        if self.head is None:
            self.head = self.tail = node
            return
        node.previous = self.tail
        self.tail.next = node
        self.tail = node

    def insertAt(self, node, index):
        self.length += 1
        current = self.head
        current_id = 0
        while current_id < index:
            current = current.next
            current_id += 1
        node.next = current
        node.previous = current.previous
        current.previous.next = node
        current.previous = node

    def popHead(self) -> Node:
        self.length -= 1
        poped = self.head
        self.head = self.head.next
        self.head.previous = None
        return poped.value

    def popEnd(self) -> Node:
        self.length -= 1
        poped = self.tail
        self.tail = self.tail.previous
        self.tail.next = None
        return poped.value

    def popAt(self, index):
        self.length -= 1
        current = self.head
        current_id = 0
        while current_id < index - 1:
            current = current.next
            current_id += 1
        current.next.previous = current.previous
        current.previous.next = current.next
        return current.value

    def getHead(self):
        return self.head.value

    def getTail(self):
        return self.tail.value

    def getAt(self, index):
        current = self.head
        current_id = 0
        while current_id < index:
            current = current.next
            current_id += 1
        return current.value


if __name__ == "__main__":
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    node4 = Node(4)
    node5 = Node(5)
    node6 = Node(6)
    node7 = Node(7)
    node8 = Node(8)
    ls = LinkedList()
    ls.prepend(node1)
    ls.prepend(node2)
    ls.prepend(node3)
    ls.prepend(node4)
    ls.prepend(node5)
    ls.prepend(node6)
    ls.append(node8)
