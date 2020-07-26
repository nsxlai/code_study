"""
Decrytping with the following rule

for a string:
1. If s[i] is lower case and s[i+1] is upper case, swap the letters and add '*'
   e.g., aTbb => Ta*bb
2. If s[i] is a number, replace it with 0 and add the original number to the beginning of the string
   e.g., ta4b => 4ta0b
3. Continue until the end of the string

If input string is 'aP5lpP4e', the encrypted output string will be '45Pa*0lPp*0e'

Create a function that will take the encrypted string and return the unencrypted string.
"""


def is_num(char):
    try:
        isinstance(int(char), int)
        return True
    except ValueError as e:
        return False


def num_char_split(str):
    """
    Splitting the input str into 2 parts: numeric str part and main str part.
    :param str:
    :return:
    """
    for char in str:
        if is_num(char):
            continue
        else:
            split_char = char
            break
    # print(f'split_char = {split_char}')
    num_str, main_str = str.split(split_char, 1)  # split only once at the split_char
    main_str = split_char + main_str  # Add the split_char back to the beginning of the main_str
    # print(f'{num_str=}, {main_str=}')
    return num_str, main_str


def decrypt(str):
    # print(f'encrypted str = {str}')
    num_str, main_str = num_char_split(str)
    work_str = ''
    skip_next_char = False
    for index, value in enumerate(main_str):
        try:
            if main_str[index].isupper() and main_str[index+1].islower() and main_str[index+2] == '*':
                work_str += main_str[index+1]
                work_str += main_str[index]
                skip_next_char = True
                continue
        except IndexError:
            pass
        if value == '0':
            work_str += num_str[-1]
            num_str = num_str[:-1]
        elif value == '*':
            continue
        elif skip_next_char:
            skip_next_char = False
            continue
        else:
            work_str += value
    return work_str


if __name__ == '__main__':
    original_str = ['aP5lpP4e', 'uMbPrrbPUM39', 'aabB0123cD', 'paTaTO']
    encrypted_str = ['45Pa*0lPp*0e', '93Mu*Pb*rrPb*UM00', '3210aaBb*0000Dc*', 'pTa*Ta*O']

    for original, encrypted in zip(original_str, encrypted_str):
        output = decrypt(encrypted)
        print(f'Encrypted str = {encrypted}')
        print(f'Decrypted str = {output}')
        if output == original:
            print(f'Algorithm decrypted successful!')
        else:
            print(f'Algorithm did not decrypt correctly...')
        print('-' * 40)
