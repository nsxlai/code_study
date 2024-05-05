# source: https://betterprogramming.pub/4-reasons-why-should-be-using-python-generators-660458b0085d

def infinite_seq():
    count = 1

    while True:
        yield count ** 2
        count = count + 1


if __name__ == '__main__':
    infinite_stream = infinite_seq()

    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))
    print(next(infinite_stream))

