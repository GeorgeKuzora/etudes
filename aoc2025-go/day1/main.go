package main

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"strconv"
)

type Direction int

const (
	Right Direction	= iota
	Left
)

type Input struct {
	Direction Direction
	StepsQnt int
}

type Dial struct {
	NSteps int
	Cur int
}

func (d *Dial) turn(direction Direction, qnt int) {
	var current int
	switch direction {
	case Right:
		current = (d.Cur + qnt) % d.NSteps
	case Left:
		current = (d.Cur - qnt + d.NSteps) % d.NSteps
	}
	d.Cur = current
}

func (d *Dial) isZero() bool {
	return d.Cur == 0
}

func main() {
	input, err := getInput("input.txt")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	dial := Dial{
		NSteps: 100,
		Cur: 50,
	}

	code := calculateCode(&dial, input)

	fmt.Println(code)
}

func getInput(path string) ([]Input, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, errors.New("can't read an input file")
	}
	defer func() {
		err := file.Close()
		if err != nil {
			fmt.Println("can't close the file")
		}
	}()

	scanner := bufio.NewScanner(file)

	out := []Input{}

	for scanner.Scan() {
		line := scanner.Text()
		out = append(out, parseInput(line))
	}
	if err := scanner.Err(); err != nil {
		return nil, errors.New("failed to parse file")
	}
	return out, nil
}

func parseInput(input string) (Input) {
	unprocessedInput := Input{
			Direction: Right,
			StepsQnt: 0,
		}

	if len(input) < 2 {
		return unprocessedInput
	}

	directionPart := string(input[0])
	var direction Direction

	switch directionPart {
	case "R":
		direction = Right
	case "L":
		direction = Left
	default:
		return unprocessedInput
	}

	qntPart := string(input[1:])

	qnt, err := strconv.Atoi(qntPart)
	if err != nil {
		return unprocessedInput
	}

	return Input {
		Direction: direction,
		StepsQnt: qnt,
	}
}

func calculateCode(dial *Dial, input []Input) int {
	code := 0

	for _, v := range input {
		dial.turn(v.Direction, v.StepsQnt)
		fmt.Println(dial.Cur)
		fmt.Println(dial.isZero())
		if dial.isZero() {
			code += 1
		}
	}

	return code
}
