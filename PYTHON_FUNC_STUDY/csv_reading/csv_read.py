# source: https://realpython.com/python-csv/

import csv

FILENAME = 'employee_birthday.txt'


def csv_open_list(file):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        # print(list(csv_reader))  # Print out the csv_reader value
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                print(f'row = {row}')
                print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
        print(f'Processed {line_count} lines.')


def csv_open_dict(file):
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            print(row)
            print(
                f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
            line_count += 1
        print(f'Processed {line_count} lines.')


if __name__ == '__main__':
    csv_open_list(FILENAME)
    print('-' * 45)
    csv_open_dict(FILENAME)