"""
WIKI: https://en.wikipedia.org/wiki/Eight_queens_puzzle
"""
"""
package main

import "fmt"

func main() {
	// stores column which queen is in for each row
	// index is row, column is value
	options := []int{0, 1, 2, 3, 4, 5, 6, 7}
	perm := getOptions(options)
	var numAns int
	for _, v := range perm {
		numAns++
		printBoard(v)
		fmt.Print("\n\n\n")
	}
	fmt.Println("Number of answers:", numAns)
}

func printBoard(board []int) {
	for y := 0; y < 15; y++ {
		if y%2 == 1 {
			fmt.Println("-+-+-+-+-+-+-+-")
		} else {
			for x := 0; x < 15; x++ {
				if x%2 == 1 {
					fmt.Print("|")
				} else {
					if board[y/2] == x/2 {
						fmt.Print("Q")
					} else {
						fmt.Print(" ")
					}
				}
			}
			fmt.Println()
		}
	}
}

func getOptions(options []int) [][]int {
	perm := permutations(options)
	ret := [][]int{}
	for _, option := range perm {
		if checkValid(option) {
			ret = append(ret, option)
		}
	}
	return ret
}

func intAbs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func checkValid(board []int) bool {
	for row1, col1 := range board {
		for row2 := row1 + 1; row2 < len(board); row2++ {
			col2 := board[row2]
			if intAbs(row2-row1) == intAbs(col2-col1) {
				return false
			}
		}
	}
	return true
}

func permutations(options []int) [][]int {
	return permute(options, 0)
}

func swap(a []int, x, y int) {
	a[x], a[y] = a[y], a[x]
}

func permute(options []int, start int) [][]int {
	answers := [][]int{}
	end := len(options) - 1
	if start == end {
		ans := make([]int, len(options))
		copy(ans, options)
		answers = append(answers, ans)
	} else {
		for i := start; i <= end; i++ {
			swap(options, start, i)
			subAnswers := permute(options, start+1)
			for _, ans := range subAnswers {
				answers = append(answers, ans)
			}
			swap(options, start, i)
		}
	}
	return answers
}
"""
from typing import List


def print_board(board: List[int]) -> None:
    for y in range(15):
        if y % 2 == 1:
            print('-+-+-+-+-+-+-+-')
        else:
            for x in range(15):
                if x % 2 == 1:
                    print('|', end='')
                else:
                    if board[y/2] == x/2:
                        print('Q', end='')
                    else:
                        print(' ', end='')
            print()


def get_options(options: List[int]) -> List[List[int]]:
    perm = _permutations(options)
    ret = []
    for option in perm:
        if check_valid(option):
            ret.append(option)
    return ret


def check_valid(board: List[int]) -> bool:
    for row1, col1 in enumerate(board):
        row2 = row1 + 1
        while row2 < len(board):
            col2 = board[row2]
            if abs(row2 - row1) == abs(col2 - col1):
                return False
            row2 += 1
    return True


def _permutations(options: List[int]) -> List[List[int]]:
    return permute(options, 0)


def _swap(arr: List[int], x: int, y: int) -> None:
    arr[x], arr[y] = arr[y], arr[x]


def permute(options: List[int], start: int) -> List[List[int]]:
    answers = []
    end = len(options) - 1

    if start == end:
        ans = options
        answers.append(ans)
    else:
        for i in range(start, end):
            _swap(options, start, i)
            subAnswers = permute(options, start+1)
            for ans in subAnswers:
                answers.append(ans)
            _swap(options, start, i)
    return answers


if __name__ == '__main__':
    """
       stores column which queen is in for each row
       index is row, column is value
    """
    options = [0, 1, 2, 3, 4, 5, 6, 7]
    perm = get_options(options)

    num_ans = 0
    for v in range(perm):
        num_ans += 1
        print_board(v)
        print('\n\n\n', end='')

    print(f'Number of answers: {num_ans}')
