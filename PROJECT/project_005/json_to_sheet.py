import json
from pprint import pprint
import pandas as pd
import numpy as np
import argparse
from typing import Any
from matplotlib import pyplot as plt


__AUTHOR__ = 'ray.lai@getcruise.com'

# Create the parser
my_parser = argparse.ArgumentParser(description='Convert JSON to Excel format')

# Add the arguments
my_parser.add_argument('-f', '--filename', type=str, help='Extract the JSON time and value and save the data to Excel')
my_parser.add_argument('-p', '--plot', type=str, help='Input the test names with the same data point for plotting.'
                                                      'E.g., -p "HW001 HW002 HW003 HW004" (space separated)')
my_parser.add_argument('-v', '--verbose', help='Display extra information for debug purpose', action='store_true')

# Execute the parse_args() method
args = my_parser.parse_args()


def workfiles() -> tuple:
    input_filename = args.filename
    # input_filename = '2021-11-15_11-07-44_P010-0005511-001_S158_Fail.json'
    output_filename = f'{input_filename.split(".")[0]}.xlsx'

    print(f'{input_filename  = }')
    print(f'{output_filename = }')
    return input_filename, output_filename


def read_json(filename: str, verbose: bool = False) -> dict:
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    if verbose:
        pprint(data)
    return data


def construct_dataframe(data: dict) -> pd.DataFrame:
    df_shape_changed = False
    df = pd.DataFrame({})
    for i in data['Test Results']:
        print(f'\n{i}: {data["Test Results"][i].get("Result")}')
        time_stamp = data['Test Results'][i].get('Time')
        print(time_stamp)
        test_value = data['Test Results'][i].get('Value')
        print(test_value)

        column_name_time = f'{i}_time'
        column_name_value = f'{i}_value'

        if type(time_stamp) is str:
            if df_shape_changed:
                time_stamp = [time_stamp] + [np.NAN] * (df.shape[0] - 1)  # Add NAN to fill the DataFrame
                test_value = [test_value] + [np.NAN] * (df.shape[0] - 1)
            else:
                time_stamp = [time_stamp]
                test_value = [test_value]
        elif type(time_stamp) is list and df_shape_changed:
            time_stamp = time_stamp + [np.NAN] * (df.shape[0] - len(time_stamp))  # Add NAN to fill the DataFrame
            test_value = test_value + [np.NAN] * (df.shape[0] - len(test_value))
        elif time_stamp is None:
            time_stamp = np.NAN
            test_value = np.NAN
        elif len(time_stamp) > 1:  # more than 1 element in the test dataset
            nan_data_list = [np.NAN] * (len(time_stamp) - df.shape[0])  # extend from the original shape to new shape
            df = df.append(nan_data_list)
            df_shape_changed = True

        df[column_name_time] = time_stamp
        df[column_name_value] = test_value
    return df


def simple_plot() -> None:
    test_fields = args.plot.split()
    df_plot = pd.DataFrame([])
    for test in test_fields:
        test_value = f'{test}_value'
        df_plot[test_value] = df[test_value]
    test_time = f'{test_fields[0]}_time'  # since all the test fields have the same time stamp, use the first one.
    df_plot.index = df[test_time]
    df_plot.plot()
    plt.show()  # Will enable the plot to stay on screen


if __name__ == '__main__':
    # The input and output files will have the same name, but different extensions (.json and .xlsx)
    input_filename, output_filename = workfiles()

    # Read JSON file
    data = read_json(input_filename, args.verbose)

    # construct Pandas DataFrame from the JSON file using time and value fields
    df = construct_dataframe(data)

    # Output the DataFrame to Excel format
    df.to_excel(output_filename)

    # Plotting
    if args.plot:
        simple_plot()
