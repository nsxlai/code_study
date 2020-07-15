"""
Given a list of strings A, find the occurrences of a given substring B
e.g.
A = ["applepie", "piecrust", "pieisforpieday"]
B = "pie"

find_occurences(A, B) -> 4
"""
import re


def find_occurences(input_list, key_str):
    """ Given a list of strings A, find the occurrences of a given substring B
    """
    occurence_count = 0
    for index, x in enumerate(input_list):
        # print 'found x and index = {}   {}'.format(index, x)
        # print 'RE result = {}'.format(re.findall(r'{}'.format(key_str), x))
        occurence_count += len(re.findall(r'{}'.format(key_str), x))
    return occurence_count


if __name__ == '__main__':
    A = ["applepie", "piecrust", "pieisforpieday"]
    B = "pie"
    print(f'Key word {B} occurrence count: {find_occurences(A, B)}')

