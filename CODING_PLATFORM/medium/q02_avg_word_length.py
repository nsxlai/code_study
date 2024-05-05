# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27


def solution(sentence: str) -> float:
    punc_list = "! ? ' , ; .".split()

    for p in punc_list:
        sentence = sentence.replace(p, ' ')
    print(sentence)
    words = sentence.split()
    return round(sum(len(word) for word in words)/len(words), 2)


if __name__ == '__main__':
    sentence1 = "Hi all, my name is Tom...I am originally from Australia."
    sentence2 = "I need to work very hard to learn more about algorithms in Python!"

    print(solution(sentence1))
    print(solution(sentence2))
