package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

func main() {
	input, err := getInput("input.txt")
	if err != nil {
		os.Exit(1)
	}
	sum := processInput(input)
	fmt.Printf("Final sum: %d\n", sum)
}

func getInput(filename string) ([]string, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer func() {
		err = file.Close()
		if err != nil {
			fmt.Println("cant close the file")
		}
	}()

	scanner := bufio.NewScanner(file)

	out := []string{}

	for scanner.Scan() {
		line := scanner.Text()
		out = append(out, line)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return out, nil
}

func processInput(input []string) int {
	sum := 0
	for _, s := range(input) {
		sum += processLine(s)
	}
	return sum
}

func processLine(line string) int {
	numOfBataries := 12
	if len(line) <= numOfBataries {
		num, err := strconv.Atoi(line)
		if err != nil {
			return 0
		}
		return num
	}

	chosen := make([]byte, numOfBataries)

	for i := 0; i < len(line) - (numOfBataries - 1); i++ {
		for j := 0; j < numOfBataries; j++ {
			if chosen[j] < line[i+j] {
				chosen[j] = line[i+j]
				for k := j+1; k < numOfBataries; k++{
					chosen[k] = line[i+k]
				}
				break
			}
		}
		if chosen[0] < line[i] {
			chosen[0] = line[i]
			chosen[1] = line[i+1]
		} else {
			if chosen[1] < line[i+1] {
				chosen[1] = line[i+1]
			}
		}
	}

	outS := ""
	for _, v := range(chosen) {
		outS += string(v)
	}
	fmt.Println(outS)
	num, err := strconv.Atoi(outS)
	if err != nil {
		return 0
	}
	return num
}
