"""
In this challenge, you will be given a list of letter heights in the alphabet and a string.
Using the letter heights given, determine the area of the rectangle highlight in mm^2 assuming
all letters are 1mm wide.

Sample Input 0
1 3 1 3 1 4 1 3 2 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5
abc

Sample Output 0
9

a=1, b=3, c=1. The tallest element is b=3 with length of 3. so the output = 9
"""


def designerPdfViewer(h, word):
    alpha_key = 'a b c e d f g h i j k l m n o p q r s t u v w x y z'.split()
    d = {}
    max_value = 0
    for i, j in zip(alpha_key, h):
        d.setdefault(i, j)

    for char in word:
        max_value = max(d[char], max_value)

    return max_value * len(word)


if __name__ == '__main__':
    h_map = '1 3 1 3 1 4 1 3 2 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 7'.split()
    h = [int(char) for char in h_map]
    word1 = 'zaba'
    word2 = 'transporter'
    print(f'highlighted area = {designerPdfViewer(h, word1)}')
    print(f'highlighted area = {designerPdfViewer(h, word2)}')
