def intToRoman(num: int) -> str:
    divisor = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    m = {1000: "M", 900: "CM", 500: "D", 400: "CD", 100: "C", 90: "XC", 50: "L", 40: "XL", 10: "X", 9: "IX", 5: "V",
         4: "IV", 1: "I"}

    ans = []
    while num > 0:
        for div in divisor:
            q = num // div
            while q > 0:
                ans.append(m[div])
                q -= 1
                num %= div
    return "".join(ans)


def intToRoman1(num: int) -> str:
    divisor = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    r_dict = {1000: 'M', 900: 'CM', 500: 'D', 400: 'CD', 100: 'C', 90: 'XC',
              50: 'L', 40: 'XL', 10: 'X', 9: 'IX', 5: 'V', 4: 'IV', 1: 'I'}
    out_str = ''

    while num > 0:
        for div in divisor:
            p = num // div
            num %= div
            while p > 0:
                out_str += r_dict[div]
                p -= 1
    return out_str


if __name__ == '__main__':
    test_list = [1993, 567, 10, 14, 98, 100, 145, 499, 990, 1024, 5678]
    for num in test_list:
        print(f'Integer {num} is Roman numerial {intToRoman(num)}')
        print(f'Integer {num} is Roman numerial {intToRoman1(num)}')