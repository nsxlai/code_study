"""
Input: "  the sky is blue "
Output: "blue is sky the"
"""


def reverse_sentence(s: str) -> str:
    # white_space = ['.',]
    s = s.strip().split()  # ['the', 'sky', 'is', 'blue']
    print(' '.join(s[::-1]))


if __name__ == '__main__':
    reverse_sentence("  the sky is blue ")
