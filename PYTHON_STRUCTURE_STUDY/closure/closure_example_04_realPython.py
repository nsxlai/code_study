"""
source: https://www.youtube.com/watch?v=BiTsdi3uSzM&t=351s

RealPython Closure Course

The NYC WIFI location data is downloaded from:
https://data.cityofnewyork.us/City-Government/NYC-Wi-Fi-Hotspot-Locations/yjub-udmw
File name: NYC_Wi-Fi_Hotspot_Locations.csv
"""
import csv
import os
from collections import Counter


def process_hotspots(file):
    def most_common_provider(file_obj):
        hotspots = []
        with file_obj as csv_file:
            content = csv.DictReader(csv_file)

            try:
                for row in content:
                    hotspots.append(row['Provider'])
            except UnicodeDecodeError as e:
                print('UnicodeDecodeError... skip to the next row')
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
    cwd = os.getcwd()
    ext = 'PYTHON_STRUCTURE_STUDY/closure'
    os.path.join(cwd, ext, file)
    process_hotspots(file)  # this example csv file has some Unicode issue and the script will stop at 176 rows
