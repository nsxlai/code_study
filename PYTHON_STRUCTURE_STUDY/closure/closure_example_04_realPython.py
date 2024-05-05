"""
source: https://www.youtube.com/watch?v=BiTsdi3uSzM&t=351s

RealPython Closure Course

The NYC WIFI location data is downloaded from:
https://data.cityofnewyork.us/City-Government/NYC-Wi-Fi-Hotspot-Locations/yjub-udmw
File name: NYC_Wi-Fi_Hotspot_Locations.csv

This file seems to have issue at line 176 (uniCodeError)
File "C:/Users/nsxla/PycharmProjects/code_study/PYTHON_STRUCTURE_STUDY/closure/closure_example_04_realPython.py", line 28, in most_common_provider
    for row in content:
  File "C:\Users\nsxla\anaconda3\lib\csv.py", line 111, in __next__
    row = next(self.reader)
  File "C:\Users\nsxla\anaconda3\lib\encodings\cp1252.py", line 23, in decode
    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 6809: character maps to <undefined>

Clean the CSV dataset with Pandas (fill in the NaN with some value):
New file: NYC_Wi-Fi_Hotspot_Locations_corrected.csv
"""
import csv
import os
from collections import Counter


def process_hotspots(file):
    def most_common_provider(file_obj):
        hotspots = []
        with file_obj as csv_file:
            content = csv.DictReader(csv_file)

            # try:
            #     for row in content:
            #         hotspots.append(row['Provider'])
            # except UnicodeDecodeError as e:
            #     print('UnicodeDecodeError... skip to the next row')
            for row in content:
                hotspots.append(row['Provider'])

        print(f'{len(hotspots) = }')
        counter = Counter(hotspots)
        print(
            f'There are {len(hotspots)} Wi-Fi hotspots in NYC.\n'
            f'{counter.most_common(1)[0][0]} has the most with '
            f'{counter.most_common(1)[0][1]}'
        )

    if isinstance(file, str):
        # Got a string-based filepath
        file_obj = open(file, 'r')
        most_common_provider(file_obj)
    else:
        # Got a file object
        most_common_provider(file)


if __name__ == '__main__':
    file = 'NYC_Wi-Fi_Hotspot_Locations.csv'
    # file = 'NYC_Wi-Fi_Hotspot_Locations_corrected.csv'
    cwd = os.getcwd()
    ext = 'PYTHON_STRUCTURE_STUDY/closure'
    os.path.join(cwd, ext, file)
    process_hotspots(file)  # this example csv file has some Unicode issue and the script will stop at 176 rows
