"""
Harold is a kidnapper who wrote a ransom note, but now he is worried it will be
traced back to him through his handwriting. He found a magazine and wants to
know if he can cut out whole words from it and use them to create an untraceable
replica of his ransom note. The words in his note are case-sensitive and he must
use only whole words available in the magazine. He cannot use substrings or
concatenation to create the words he needs.

Given the words in the magazine and the words in the ransom note, print Yes if
he can replicate his ransom note exactly using whole words from the magazine;
otherwise, print No.

For example, the note is "Attack at dawn". The magazine contains only "attack
at dawn". The magazine has all the right words, but there's a case mismatch.
The answer is No.
"""
# Complete the checkMagazine function below.
def checkMagazine(magazine, note):
    d = {}
    for word in magazine:
        d.setdefault(word, 0)
        d[word] += 1
    # print('d1 = {}'.format(d))

    result = 'Yes'
    for word in note:
        if word in d:
            d[word] -= 1
            if d[word] == 0:
                del d[word]
            # print('d2 = {}'.format(d))
        else:
            result = 'No'
    print(result)


if __name__ == '__main__':
    magazine1 = 'give me one grand today night'
    note1 = 'give one grand today'
    checkMagazine(magazine1, note1)
