"""
The Utopian Tree goes through 2 cycles of growth every year. Each spring, it doubles in height. Each summer,
its height increases by 1 meter.

Laura plants a Utopian Tree sapling with a height of 1 meter at the onset of spring. How tall will her tree
be after  growth cycles?

For example, if the number of growth cycles is , the calculations are as follows:

Period  Height
0          1    (initial height)
1          2    (double at Spring)
2          3    (add 1 m at Summer)
3          6    (double at Spring)
4          7    (add 1 m at Summer)
5          14   (double at Spring)

Need to build a sequence with specific pattern: 1, 2, 3, 6, 7 14, 15, 30, 31, 62...
This is similar to the Fibonacci sequence, where the nth element depends on the previous elements
"""


def utopianTree(n):
    if n == 0:
        return 1

    if n % 2 == 0:  # even index element (2, 4, 6, 8, 10...)
        height = utopianTree(n-1) + 1
    else:  # odd index element (1, 3, 5, 7, 9...)
        height = utopianTree(n-1) * 2
    return height


if __name__ == '__main__':
    test_case = [2, 6]
    for num in test_case:
        print(f'{num}\t{utopianTree(num)}')
    print('-' * 10)
    print(utopianTree(2))
