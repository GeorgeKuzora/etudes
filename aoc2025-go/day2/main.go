package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	inputBytes, err := getText("input.txt")
	if err != nil {
		os.Exit(1)
	}
	inputText := string(inputBytes)
	ranges := strings.Split(inputText, ",")
	sum := 0
	for _, r := range(ranges) {
		sum += processRange(r)
	}
	fmt.Printf("final sum: %d\n", sum)
}

func getText(filename string) ([]byte, error) {
	file, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	return file, nil
}

func processRange(r string) int {
	r = strings.Trim(r, "\n")
	idxs := strings.Split(r, "-")

	if len(idxs) < 2 {
		return 0
	}
	str1 := idxs[0]
	str2 := idxs[1]
	sum := 0

	num1, _ := strconv.Atoi(str1)
	num2, _ := strconv.Atoi(str2)

	for i := num1; i <= num2; i++ {
		if isInvalidId(i) {
			sum += i
		}
	}
	return sum
}

func isInvalidId(id int) bool {
	s := strconv.Itoa(id)
	if len(s) < 2 {
		return false
	}
	last := len(s)
	windowLen := 1
	for {
		arrayOfSlices := []string{}
		index := 0
		for {
			slice := s[index:min(index+windowLen, last)]
			arrayOfSlices = append(arrayOfSlices, slice)
			if index+windowLen >= last { break }
			index+=windowLen
		}

		if AllEqual(arrayOfSlices) {
			fmt.Printf("Slices: %v, Id: %d\n", arrayOfSlices, id)
			fmt.Println(AllEqual(arrayOfSlices))
			return true
		}

		if windowLen*2 > last {
			break
		}
		windowLen++
	}
	return false
}

func AllEqual(arrayOfSlices []string) bool {
	first := arrayOfSlices[0]
	if len(arrayOfSlices) < 2 {
		return false
	}
	for _, v := range(arrayOfSlices[1:]) {
		if v != first {
			return false
		}
	}
	return true
}
