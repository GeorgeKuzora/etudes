def partition(array: list[int], lo: int, hi: int) -> int:
    pivot: int = array[hi]
    id = -1
    for i in range(len(array)):
        if array[i] < pivot:
            id += 1
            array[i], array[id] = array[id], array[i]
    id += 1
    array[hi], array[id] = array[id], array[hi]
    return id


def qs(array: list[int], lo, hi) -> None:
    if lo >= hi:
        return
    pivot = partition(array, lo, hi)
    qs(array, lo, pivot-1)
    qs(array, pivot+1, hi)


def quickSort(array, start, end):
    left = start
    right = end

    middle = array[(start + end) // 2]

    while left <= right:
        while array[left] < middle:
            left += 1

        while array[right] > middle:
            right -= 1

        if left <= right:
            if left < right:
                buf = array[left]
                array[left] = array[right]
                array[right] = buf
            left += 1
            right -= 1

    if left < end:
        quickSort(array, left, end)

    if start < right:
        quickSort(array, start, right)


def quick(array, lo, hi):
    pivot_id = (lo + hi) // 2
    pivot_v = array[pivot_id]
    start = lo
    end = hi
    while start <= end:
        while array[start] < pivot_v:
            start += 1
        while array[end] > pivot_v:
            end -= 1
        if start <= end:
            if start < end:
                array[start], array[end] = array[end], array[start]
            start += 1
            end -= 1
    if start < hi:
        quick(array, start, hi)
    if lo < end:
        quick(array, lo, end)


if __name__ == "__main__":
    array = [3, 2, -1, 10, 51, 12, -7, -8, 23, 4, 2, 1]
    print(array)
    quick(array, 0, len(array) - 1)
    print(array)
