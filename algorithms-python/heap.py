class MinHeap:
    def __init__(self, data=[]) -> None:
        self.lenght = len(data)
        self.data = data

    def make_heap(self) -> None:
        middle = self.lenght // 2 - 1
        for i in range(middle, -1, -1):
            self.heapify_down(i)
  def sort(self) -> None:
        for i in range(self.lenght - 1, 0, -1):
            self.data[0], self.data[i] = self.data[i], self.data[0]
            self.heapify_up(0)

    def insert(self, value: int) -> bool:
        self.lenght += 1
        self.data.append(value)
        self.heapify_up(self.lenght - 1)
        return True

    def pop(self) -> int | None:
        if self.lenght == 0:
            raise IndexError
        out = self.data[0]
        self.lenght -= 1
        if self.lenght == 0:
            self.data = []
            return out
        self.data[0] = self.data.pop(-1)
        self.heapify_down(0)
        return out

    def update(self, value) -> None:
        pass

    def left_child(self, id: int) -> int:
        return id * 2 + 1

    def right_child(self, id: int) -> int:
        return id * 2 + 2

    def parent(self, id: int) -> int:
        return (id - 1) // 2

    def heapify_up(self, id: int) -> None:
        if id <= 0:
            return
        parent_id: int = self.parent(id)
        if self.data[id] < self.data[parent_id]:
            self.swap(id, parent_id)
            self.heapify_up(parent_id)

    def heapify_down(self, id: int) -> None:
        left_id = self.left_child(id)
        right_id = self.right_child(id)
        if id > self.lenght - 1 or left_id > self.lenght - 1:
            return
        left_value = self.data[left_id]
        right_value = self.data[right_id]
        value = self.data[id]
        if left_value > right_value and value > right_value:
            self.swap(id, right_id)
            self.heapify_down(right_id)
        elif left_value < right_value and value > left_value:
            self.swap(id, left_id)
            self.heapify_down(left_id)

    def swap(self, curr_id: int, next_id: int) -> None:
        self.data[next_id], self.data[curr_id] = self.data[curr_id], self.data[next_id]


if __name__ == "__main__":
    heap = MinHeap([3, 5, 8, -1, 0, 39, -30, 9, 7, 2, 11])
    heap.make_heap()
    print(heap.data)
    heap.sort
    print(heap.data)
    heap.insert(6)
    print(heap.data)
    print(heap.pop())
    print(heap.data)
