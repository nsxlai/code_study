from datetime import datetime


if __name__ == '__main__':

    today = datetime.today()
    a = 0x10

    print(f"Today is {today}")
    print(f"Today is {today:%B %d, %Y}")
    print(f"Today is {today:%m-%d-%Y}")

    print(f'{a = }')
    print(f'a:x = {a:x}')
    print(f'a:o = {a:o}')
    print(f'a:b = {a:b}')
