# Reverse a string that has only letters, anything else should be in the same position
# example -> 'abc-'
# output -> 'cba-'

# example -> 'abd*i'
# output -> 'idb*a'

# example -> 'abc*def-hijk*'
# output  -> 'kji*hfe-dcba*'

# could be multiple (>2) non-alpha characters in the string
# isalpha(s: str): bool


# []
# '-abc'

def reverse_alpha(s: str) -> str:
    s_list = list(s)
    i, j = 0, 0
    while i < len(s_list) // 2 and j <= len(s_list) // 2:
        # all([s_list[i].isalpha(), s_list[len(s_list)-1-j].isalpha()])
        if s_list[i].isalpha() and s_list[len(s_list) - 1 - j].isalpha():
            s_list[i], s_list[len(s_list) - 1 - j] = s_list[len(s_list) - 1 - j], s_list[i]
            i += 1
            j += 1
        elif not s_list[i].isalpha():
            i += 1
        elif not s_list[len(s_list) - 1 - j].isalpha():
            j += 1

    return ''.join(s_list)


def reverse_alpha_rf(s: str) -> str:
    """
    More readable code here
    """
    sl = list(s)
    i, j = 0, len(sl)-1
    while i < (len(sl) // 2) <= j:
        if sl[i].isalpha() and sl[j].isalpha():
            sl[i], sl[j] = sl[j], sl[i]
            i += 1
            j -= 1
        elif not sl[i].isalpha():
            i += 1
        elif not sl[j].isalpha():
            j -= 1
    return ''.join(sl)


if __name__ == '__main__':
    test_list = ['abc-', 'abd*i', 'abc*def-hijk*', '-abc']
    for test in test_list:
        print(f'Original = {test}')
        print(f"reverse_alpha = {reverse_alpha(test)}")
        print(f"reverse_alpha_rf = {reverse_alpha_rf(test)}")
        print('-' * 30)
