"""
source: https://www.youtube.com/watch?v=lfQvPHGtu6Q&t=628s
From Tech with Tim channel

source: https://www.geeksforgeeks.org/greedy-algorithms/

Fractional Knapsack Problem
Problem statement:
The backpack has capacity (size) of 25. Find the maximum value of the item that can be fit into the backpack.
The items can be subdivided to fill the backpack. Also each item can only be used once.

Backpack Capacity = 25
Item    Size    Value   Value/Size
0       22      19      19/22 = 0.8636
1       10      9       9/10 = 0.9
2       9       9       9/9 = 1
3       7       6       6/7 = 0.857

The v/s ratio is the highest for item 2. Will prioritize the v/s ratio from the highest to lowest
** Real world example will be stock trading with fix amount of money to maximize the stock value.

The limitation of the greedy algorithm is that if we cannot subdivide the item, the value/size ratio will not make
sense and the algorithm cannot delivery the best solution.

Dynamic programming may be a better solution if we cannot subdivide the item value.
"""
import math


if __name__ == '__main__':
    # input format: Dict[item, Tuple[value, size]}
    arr = {0: (19, 22), 1: (9, 10), 2: (9, 9), 3: (6, 7)}

    v_ratio = []
    for item, val_size_pair in arr.items():
        fp = round(val_size_pair[0] / val_size_pair[1], 3)
        v_ratio.append(fp)

    previous_size = 0
    current_size = 0
    previous_value = 0
    current_value = 0
    total_value = 0
    max_size = 25
    fraction_multiplier = 1  # between 0 and 1
    while len(v_ratio) >= 0:
        v_ratio_max = max(v_ratio)
        idx = v_ratio.index(v_ratio_max)
        previous_size, previous_value = current_size, current_value
        current_value += arr.get(idx)[0]
        current_size += fraction_multiplier * arr.get(idx)[1]
        print(f'Adding item {idx} with value {arr.get(idx)[0]} and size {arr.get(idx)[1]} with {fraction_multiplier*100:.2f}%')

        if current_size > max_size:
            current_size, current_value = previous_size, previous_value
            fraction_multiplier = round(((max_size - current_size) / arr.get(idx)[1]), 3) - 0.001  # round to the 3 decimal places
            print(f'This item is too large in size; reduce the size to fraction {fraction_multiplier} of item {idx}')
            continue
        elif round(abs(max_size - current_size), 2) < 0.10:  # to account for very small rounding difference due to floating point ops
            break

        v_ratio.remove(v_ratio_max)  # remove the max ratio for this loop
        del(arr[idx])

    print(f'The fill size is {current_size}')
    print(f'The value is {current_value}')