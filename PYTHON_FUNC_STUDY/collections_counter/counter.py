from collections import defaultdict, Counter


WORD = 'mississippi'


def count_method_1(word: str) -> None:
    counter = {}
    for letter in word:
        if letter not in counter:
            counter[letter] = 0
        counter[letter] += 1
    print(f'Method 1 {counter = }')


def count_method_2(word: str) -> None:
    """ Use .get dict method """
    counter = {}
    for letter in word:
        counter[letter] = counter.get(letter, 0) + 1
    print(f'Method 2 {counter = }')


def count_method_3(word: str) -> None:
    """ Use defaultdict """
    counter = defaultdict(int)  # Set up a default dict with int as element, create the key if not there
    for letter in word:
        counter[letter] += 1
    print(f'Method 3 {counter = }')


if __name__ == '__main__':
    count_method_1(WORD)
    count_method_2(WORD)
    count_method_3(WORD)

    # Using Counter
    print(f'{Counter(WORD) = }')  # input is a string
    print(f'{Counter(list(WORD)) = }')  # input is a list
    print(f'{Counter({"i": 4, "s": 4, "p": 2, "m": 1}) = }')  # input is a dict
    print(f'{Counter(i=4, s=4, p=2, m=1) = }')  # keyword argument
    print(f'{Counter(set("mississippi")) = }')  # input is a set, set only hold 1 unique value count for the key

    print(f'{Counter(apple=10, orange=15, banana=0, tomato=-15) = }')

    letters = Counter('mississippi')
    print(f'{letters = }')
    letters.update('ohio')
    print(f'{letters = }')
    letters.update({'i': 37, 'h':-5})
    print(f'{letters = }')
    letters.update(s=5, p=5)
    print(f'{letters = }')

    print(f'{letters.keys() = }')
    print(f'{letters.values() = }')

    print(f'{letters["a"] = }')  # Return the count of letter "a", this is a different behavior than regular dict
    print(f'{letters.most_common() = }')
    print(f'{letters.most_common(2) = }')  # Returns only 2 items

    # least common
    least_common_letter = letters.most_common()
    least_common_letter.reverse()
    print(f'{least_common_letter = }')

    # or
    least_common_letter = letters.most_common()
    least_common_letter = reversed(list(least_common_letter))
    print(f'{least_common_letter = }')

    # or
    print(f'{letters.most_common()[::-1] = }')

    # Merging 2 dictionaries
    a = {'a': 3, 'b': 5, 'c': 10}
    b = {'b': 20, 'c': 50, 'd': 60}
    c = {**a, **b}
    print(f'{c = }')
