package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	input, err := getInput("input.txt")
	if err != nil {
		os.Exit(1)
	}
	processed1 := parseSimple(input)
	total1 := sumColumns(processed1)

	processed2 := parseHard(input)
	total2 := sumColumns(processed2)

	fmt.Printf("Part1 total: %d\nPart2 total: %d\n", total1, total2)
}

func getInput(filename string) ([]string, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer func() {
		err = file.Close()
		if err != nil {
			os.Exit(2)
		}
	}()

	var out []string

	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		line := strings.Trim(scanner.Text(), "\n")
		if line == "" {
			continue
		}
		out = append(out, line)
	}

	if err = scanner.Err(); err != nil {
		return nil, err
	}
	return out, nil
}

func parseSimple(input []string) [][]string {
	var columns [][]string
	for _, line := range input {
		fields := strings.Fields(line)

		if len(columns) == 0 {
			columns = make([][]string, len(fields))
		}

		for i, s := range fields {
			column := columns[i]
			columns[i] = append(column, s)
		}
	}
	return columns
}

func parseHard(input []string) [][]string {
	emptyColIdMap := make(map[int]bool)

	columnLenMap := []int{}
	colStart := 0
	colEnd := 0
	emptyColId := -1

	opString := input[len(input)-1]
	for i, op := range(opString) {
		if op != ' ' {
			if emptyColId == -1 {
				emptyColId = 0
				continue
			}
			emptyColId := i - 1
			emptyColIdMap[emptyColId] = true

			colEnd = i - 1
			colLen := colEnd - colStart
			columnLenMap = append(columnLenMap, colLen)
			colStart = i
		}
	}
	colLen := len(opString) - colStart
	columnLenMap = append(columnLenMap, colLen)

	fmt.Println(columnLenMap)
	out := make([][]string, len(columnLenMap))
	for i := range out {
		out[i] = make([]string, columnLenMap[i])
	}

	for _, s := range input[:len(input)-1] {
		curColumnId := 0
		curColStart := 0

		for j, c := range s {
			if emptyColIdMap[j] {
				curColumnId++
				curColStart = j + 1
				continue
			} else if c == ' ' {
				continue
			} else {
				num := out[curColumnId][j-curColStart]
				out[curColumnId][j-curColStart] = num + string(c)
			}
		}
	}

	curColId := 0
	for _, op := range input[len(input)-1] {
		if op != ' ' {
			out[curColId] = append(out[curColId], string(op))
			curColId++
		}
	}

	fmt.Println(out)
	return out
}

func sumColumns(columns [][]string) int {
	total := 0
	for _, col := range columns {
		res := processCol(col)
		total += res
	}
	return total
}

func processCol(col []string) int {
	var total int

	op := col[len(col) - 1]
	if op == "+" {
		total = 0
		for _, b := range col[:len(col)-1] {
			s := string(b)
			n, _ := strconv.Atoi(s)
			total += n
		}
	} else if op == "*" {
		total = 1
		for _, b := range col[:len(col)-1] {
			s := string(b)
			n, _ := strconv.Atoi(s)
			total *= n
		}
	}
	return total
}
