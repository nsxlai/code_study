"""
source: https://www.interviewquery.com/questions/last-page-number?ref=question_email

Write a function get_last_page to return the last page number in the string.
If the string of integers is not in correct page order, return the last number in order.

Examples:
input = '12345'
output = 5

input = '12345678910111213'
output = 13

input = '1235678'
output = 3
"""
from pytest import mark


def get_last_page(int_string):
    # set counter
    i = 0

    # while there is still a string
    while len(int_string) > 0:
        i += 1
        # compare our index to the page number
        # we have to do an operation where we cut the value by the length of the digit
        # for example '11', we have to cut off two digits
        if i == int(int_string[:len(str(i))]):
            # recreate the integer string
            int_string = int_string[len(str(i)):]
        else:
            # if it's not equivalent, return the last index number
            return i - 1
    return i


test_list = [('12345', 5), ('12345678910111213', 13), ('1235678', 3)]


@mark.parametrize('page_list, page_end', test_list)
def test_get_last_page(page_list, page_end):
    f_out = get_last_page(page_list)
    assert f_out == page_end
