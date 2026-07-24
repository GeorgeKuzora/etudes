from dataclasses import dataclass

dir = (
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
)


@dataclass
class Point:
    x: int = 0
    y: int = 0


def printTable(table):
    for i in range(len(table)):
        for j in range(len(table[0])):
            print(f"{table[i][j]}", end=" ")
        print()


def solve(table):
    count = 0
    seen = []
    point = Point(y=0, x=0)
    table, end = walk(table, point, seen, count, dir[0])
    return table


def walk(table, point, seen, count, end=False):
    if count >= len(table) * len(table[0]):
        return table, True
    if point.x < 0 or point.x >= len(table[0]) or point.y < 0 or point.y >= len(table):
        return (
            table,
            False,
        )
    if point in seen:
        return table, False

    # Pre
    table[point.y][point.x] = count
    seen.append(point)
    # Recursive
    for d in dir:
        y, x = d
        table, end = walk(
            table, Point(x=point.x + x, y=point.y + y), seen, count + 1, end
        )
        if end:
            return table, True
    # Post


if __name__ == "__main__":
    table = []
    for i in range(15):
        row = []
        for j in range(15):
            row.append(0)
        table.append(row)
    new_table = solve(table)
    printTable(new_table)
