package main

import (
	"bytes"
	"fmt"
	"os"
)

type Type byte

const (
	roll = Type('@')
	empty = Type('.')
)

type Item struct {
	t Type
	x int
	y int
}

func (i Item) isEmpty() bool {
	return i.t == empty
}

type Direction struct {
	x int
	y int
}

var (
	NW = Direction{x: -1, y: -1}
	N = Direction{x: 0, y: -1}
	NE = Direction{x: 1, y: -1}
	E = Direction{x: 1, y: 0}
	SE = Direction{x: 1, y: 1}
	S = Direction{x: 0, y: 1}
	SW = Direction{x: -1, y: 1}
	W = Direction{x: -1, y: 0}
)

var directions = []Direction{NW, N, NE, E, SE, S, SW, W}


type Field struct {
	rows int
	cols int
	field *[][]byte
}

func NewField(input [][]byte) Field {
	if len(input) == 0 {
		return Field{
			field: &input,
		}
	}
	return Field {
		rows: len(input),
		cols: len(input[0]),
		field: &input,
	}
}

func (f *Field) isAccessible(item Item) bool {
	requiredToBlock := 4
	blocked := 0

	for _, dir := range(directions) {
		if f.isBlocked(item, dir) {
			blocked += 1
		}
		if blocked >= requiredToBlock {
			return false
		}
	}
	return true
}

func (f *Field) isBlocked(item Item, dir Direction) bool {
	newX := item.x + dir.x
	newY := item.y + dir.y
	if newX > f.cols - 1 || newX < 0 || newY > f.rows - 1 || newY < 0 {
		return false
	}
	field := *f.field
	newChar := field[newY][newX]
	newItem := Item{
		t: Type(newChar),
		x: newX,
		y: newY,
	}
	return !newItem.isEmpty()
}

func (f *Field) remove(item Item) {
	field := *f.field
	field[item.y][item.x] = byte(empty)
}

func main() {
	input, err := getInput("input.txt")
	if err != nil {
		os.Exit(1)
	}

	field := NewField(input)

	out := processField(&field)

	fmt.Printf("Final result: %d\n", out)
}

func getInput(filename string) ([][]byte, error) {
	file, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	lines := bytes.Split(file, []byte("\n"))

	if len(lines) > 0 && len(lines[len(lines)-1]) == 0 {
    	lines = lines[:len(lines)-1]
	}
	return lines, nil
}

func processField(field *Field) int {
	total := 0
	for {
		hadAccessible := false
		for i, line := range(*field.field) {
			for j, char :=range(line) {
				item := Item{
					t: Type(char),
					x: j,
					y: i,
				}
				if item.isEmpty() {
					continue
				}

				if field.isAccessible(item) {
					field.remove(item)
					total += 1
					hadAccessible = true
				}
			}
		}
		if !hadAccessible {
			break
		}
	}
	return total
}
