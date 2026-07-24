package main

import (
	"bufio"
	"cmp"
	"fmt"
	"os"
	"slices"
	"strconv"
	"strings"
)

type Input struct {
	Ranges []string
	Items []string
}

type Item int

type Range struct {
	left int
	right int
}

func NewRange(in string) Range {
	s := strings.Split(in, "-")
	zero, _ := strconv.Atoi(s[0])
	one, _ := strconv.Atoi(s[1])
	left := min(zero, one)
	right := max(zero, one)
	return Range{left: left, right: right}
}

func CompareByLeftBorder(a, b Range) int {
	leftCompare := cmp.Compare(a.left, b.left)
	if leftCompare != 0 {
		return leftCompare
	}
	return cmp.Compare(a.right, b.right)
}

func ComparItemInRange(r Range, i Item) int {
	integer := int(i)
	if integer <= r.right && integer >= r.left {
		return 0
	}
	if integer > r.right {
		return -1
	}
	if integer < r.left {
		return 1
	}
	return 0
}

func main() {
	input, err := getInput("input.txt")
	if err != nil {
		os.Exit(1)
	}

	var items []Item
	for _, i := range(input.Items) {
		integer, _ := strconv.Atoi(i)
		items = append(items, Item(integer))
	}

	var ranges []Range
	for _, i := range(input.Ranges) {
		r := NewRange(i)
		ranges = append(ranges, r)
	}

	slices.SortFunc(ranges, CompareByLeftBorder)

	fmt.Println("Sorted ranges")
	for _, r := range(ranges) {
		fmt.Println(r)
	}
	fmt.Println()

	combinedRanges := combineRanges(ranges)

	fmt.Println()

	fmt.Println("Combined ranges")
	for _, r := range(combinedRanges) {
		fmt.Println(r)
	}
	fmt.Println()

	count := CountItemInRanges(items, combinedRanges)
	fmt.Printf("Final count: %d\n", count)

	// PART 2
	allRangesCount := 0

	for _, r := range(combinedRanges) {
		inRange := r.right - r.left + 1
		allRangesCount += inRange
	}

	fmt.Println()
	fmt.Printf("All ranges count: %d\n", allRangesCount)
}

func combineRanges(ranges []Range) []Range {
	cri := 0
	nri := cri + 1
	var out []Range

	for cri < len(ranges) {
		cr := ranges[cri]
		comb := Range{left: cr.left, right: cr.right}

		for nri < len(ranges){
			nr := ranges[nri]

			if comb.right < nr.left {
				break
			} else if comb.right >= nr.left && comb.right <= nr.right {
				comb.right = nr.right
				cri += 1
				nri += 1
			} else if comb.right >= nr.left && comb.right > nr.right {
				cri += 1
				nri += 1
			}
		}

		out = append(out, comb)
		cri += 1
		nri += 1
	}
	return out
}

func getInput(filename string) (Input, error) {
	file, err := os.Open(filename)
	if err != nil {
		return Input{}, err
	}

	scanner := bufio.NewScanner(file)

	input := Input{}

	isRanges := true

	for scanner.Scan() {
		line := scanner.Text()
		if len(line) == 0 {
			isRanges = false
			continue
		}
		if isRanges {
			input.Ranges = append(input.Ranges, line)
		} else {
			input.Items = append(input.Items, line)
		}
	}

	if err := scanner.Err(); err != nil {
		return Input{}, err
	}
	return input, nil
}

func CountItemInRanges(items []Item, ranges []Range) int {
	count := 0

	for _, i := range(items) {
		_, found := slices.BinarySearchFunc(ranges, i, ComparItemInRange)
		if found {
			count += 1
		}
	}
	return count
}
