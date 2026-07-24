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

func (d *Dial) turn(direction Direction, qnt int) int {

	var timesCrossZeros int

	switch direction {
	case Right:
		timesCrossZeros = (d.Cur + qnt) / d.NSteps
	case Left:
		relativeToZero := d.Cur - qnt
		if relativeToZero > 0 {
			timesCrossZeros = 0
		} else if relativeToZero == 0 {
			timesCrossZeros = 1
		} else {
			if d.isZero() {
				timesCrossZeros = (relativeToZero * -1) / d.NSteps
			} else {
				timesCrossZeros = (relativeToZero * -1 + d.NSteps) / d.NSteps
			}
		}
	}

	d.calcCur(direction, qnt)

	return timesCrossZeros
}

func (d *Dial) calcCur(direction Direction, qnt int) {
	var current int
	switch direction {
	case Right:
		current = (d.Cur + qnt) % d.NSteps
	case Left:
		current = ((d.Cur - qnt) + d.NSteps) % d.NSteps
		if current < 0 {
			current += d.NSteps
		}
	}
	d.Cur = current
	fmt.Println(d.Cur)
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

	fmt.Println("answer")
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
		zeros := dial.turn(v.Direction, v.StepsQnt)
		code += zeros
	}

	return code
}
