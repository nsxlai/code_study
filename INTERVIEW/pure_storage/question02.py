"""
Questions: list of the IP addresses in a given file

Test cases:
1. Use a valid IP address (all) in the test.txt
2. Use an invalid IP address (mixed with valid IP addresses) in test.txt
   2.1. Invalid could mean IP range outside < 0 or > 255
   2.2. Invalid could mean given a string instead of number
   2.3. Use float numbers instead of integer (should float convert to integer automatically or not)
3. test.txt is blank (0-byte file)
4. test.txt is extra large (more than 4GB)
5. Test the function across different Python versions 3.0 to 3.8 (3.9 coming)

Feature:
1. Future proofing: should IP v6 be supported


Difference between re.match and re.search:
Python offers two different primitive operations based on regular expressions:
    1. match checks for a match only at the beginning of the string
    2. search checks for a match anywhere in the string
"""
import re


def extract_ip_addr(file_name):
    with open(file_name, 'r') as f:
        f_out = f.read()

    result = re.findall(r'[\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}', f_out)
    return result


if __name__ == '__main__':
    file_name = 'ip_addr.txt'
    ip_addr = extract_ip_addr(file_name)
    print(f'{ip_addr = }')
