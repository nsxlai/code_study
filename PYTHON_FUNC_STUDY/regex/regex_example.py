"""
https://docs.python.org/3/library/re.html
https://regex101.com/
https://docs.microsoft.com/en-us/dotnet/standard/base-types/regular-expression-language-quick-reference
"""
import re


if __name__ == '__main__':
    input_str = '[)>RS06GSY8161302000000XGSP1X391433AGS12V000000000GST1121045012RSEOT'

    # Method 1
    vpps = re.search(r'GSY(\w+)XGS', input_str)
    print(f'{vpps.group(0) = }')
    print(f'{vpps.group(1) = }')
    vpps = vpps.group(1)

    # Method 2
    pattern = re.compile(r'GSP(\w+)GS12V')
    pn = pattern.search(input_str)
    print(f'{pn.group(0) = }')
    print(f'{pn.group(1) = }')
    pn = pn.group(1)

    duns = re.search(r'12V(\w+)GST', input_str)
    print(f'{duns.group(0) = }')
    print(f'{duns.group(1) = }')
    duns = duns.group(1)

    sn = re.search(r'GST(\w+)RSEOT', input_str)
    print(f'{sn.group(0) = }')
    print(f'{sn.group(1) = }')
    sn = sn.group(1)

    product_info = {'vpps': vpps, 'pn': pn, 'duns': duns, 'sn': sn}
    print(f'{product_info = }')
