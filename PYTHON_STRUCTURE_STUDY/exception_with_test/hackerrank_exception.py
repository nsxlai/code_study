class Calculator:
    def power(self, n, p):
        try:
            if n < 0 or p < 0:
                raise ValueError('n and p should be non-negative')
            else:
                if p == 0:
                    return 1
                else:
                    temp = n
                    for i in range(1, p):
                        temp = temp * n
                    return temp
        except (ValueError, TypeError) as e:
            return e


if __name__ == '__main__':
    myCalculator = Calculator()
    test_values = [(3, 5), (2, 4), (-1, -2), (-1, 3), (4, -2), (4, 2), ('3', '5')]
    for n, p in test_values:
        ans = myCalculator.power(n, p)
        print(ans)
        # print(type(ans))
