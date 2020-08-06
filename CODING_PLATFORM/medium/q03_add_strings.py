# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27


def solution1(num1: str, num2: str) -> str:
    return str(eval(num1) + eval(num2))


def solution2(num1: str, num2: str) -> str:
    n1, n2 = 0, 0
    m1, m2 = 10**(len(num1)-1), 10**(len(num2)-1)

    for i in num1:
        # print(f'{n1=}, {m1=}, {ord(i)=}, {ord("0")=}')
        n1 += (ord(i) - ord('0')) * m1
        m1 = m1 // 10

    for i in num2:
        n2 += (ord(i) - ord('0')) * m2
        m2 = m2 // 10

    return str(n1 + n2)


if __name__ == '__main__':
    num1 = '364'
    num2 = '1836'
    print(solution1(num1, num2))
    print(solution2(num1, num2))
