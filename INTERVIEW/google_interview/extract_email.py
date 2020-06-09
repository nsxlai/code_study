"""
This python script will open a file and extract email addresses and output it to a file
"""
import re

if __name__ == '__main__':
    with open('test_file.txt', 'r') as f:
        file_output = f.read()   # read all the text at once as a string

    regex_str = '[\w+\.\-]+@[\w\.\-]+'
    email_list = re.findall(regex_str, file_output)
    print(email_list)

    # output the email to a new file
    with open('test_email_output.txt', 'w') as nf:
        for email in email_list:
            nf.writelines(email + '\n')
