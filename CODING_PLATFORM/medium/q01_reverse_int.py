# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27


def solution(x: int) -> int:
    string = str(x)

    try:
        if string[0] == '-':
            return int('-' + string[:0:-1])
        else:
            return int(string[::-1])
    except ValueError:
        print('Incorrect input format. Need to use integer value')


if __name__ == '__main__':
    print(solution(0))
    print(solution(-43566))
    print(solution(9000))
    print(solution('testing'))
