class Solution:
    def convert(self, s: str, numRows: int) -> str:
        """
        Two circumstances:
            1. First and last row, get character in step of step = 2*numRows - 2
            2. Other rows, step of 1st and 2nd character is step-2*row_num, step of
               2nd and 3rd is character 2*row_num, 3rd and 4th is step-2*row_num again, etc.
        :param s:
        :param numRows:
        :return: out_str (str)
        """
        length = len(s)
        if numRows == 1 or numRows >= length:
            return s

        step = 2 * numRows - 2
        print(f'{step=}')
        ret = ""
        for i in range(0, numRows):
            j = i
            step_one = step - 2 * i
            print('-' * 15)
            print(f'{step_one=}')
            while j < length:
                ret += s[j]
                print(f'{j=}; {ret=}')
                if i == 0 or i == numRows - 1:
                    j += step
                    print(f'Adding Step; {j=}, {step=}')
                else:
                    j += step_one
                    print(f'Adding Step_ONE; {j=}, {step_one=}')
                    # If it's not first or last row, you need to change step after get one character
                    step_one = step - step_one
                    print(f'Final; {step=}, {step_one=}')
        return ret


if __name__ == '__main__':
    s = Solution()
    out = s.convert('paypalishiring', 4)
    print('{}'.format(out))
