"""
Github source: https://github.com/bcollazo/catanatron
Youtube source: https://www.youtube.com/watch?v=Vg4JLbxVuFA&t=25s
"""
import pandas as pd

if __name__ == '__main__':
    file_name = 'NYC_Wi-Fi_Hotspot_Locations.csv'
    df = pd.read_csv(file_name)

    print(f'{df.shape = }')
    print(f'{df.isnull().sum() = }')
    print(f'{df[df.isnull().any(axis=1)] = }')
    df.fillna(0, inplace=True)
    print(f'{df.isnull().sum() = }')
