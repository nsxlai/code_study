

if __name__ == '__main__':
    book = 'this is a book. this is a very long book and there will be a lot of interest about this book.'
    words = book.split()

    d = {}
    for word in words:
        d.setdefault(word, 0)
        d[word] += 1

    print(f'{d = }')
    # sorted(d, key=d.get)
    print(dict(sorted(d.items(), key=lambda item: item[1], reverse=True)))  # highest value first

    # dict(sorted(people.items(), key=lambda item: item[1]))
