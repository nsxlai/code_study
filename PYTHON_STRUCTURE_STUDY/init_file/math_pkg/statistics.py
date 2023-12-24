
def mean(a: list) -> float:
    return sum(a) / len(a)


def median(a: list) -> int:
    a.sort()
    median_index = len(a) // 2
    return a[median_index]


if __name__ == '__main__':
    t = median([4, 2, 7, 20, 8, 12])
    print(f'{t = }')