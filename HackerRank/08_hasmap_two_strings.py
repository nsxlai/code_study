
def twoStrings(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    if set1 & set2 != set():
        result = 'YES'
    else:
        result = 'NO'
    return result


if __name__ == '__main__':
    s1 = 'hello'
    s2 = 'world'
    result = twoStrings(s1, s2)
    print(result)
    assert result == 'YES'  # 'o' and 'l' are in both string
