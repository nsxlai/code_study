"""
source: https://medium.com/@jacob.d.moore1/dynamic-programming-in-python-a7bd71345762

The Robber Problem
There’s a robber in a neighborhood. He (or she!) wants to maximize loot and knows two key facts (1)
The value of loot in each home and (2) that no two adjacent homes can be looted without activation
of a neighborhood security alarm.

If the robber loots the first home, he cannot visit the second but must skip to third. If the robber
does not loot the first home, he can loot the second. This rule is constantly true for any home in
the sequence. At every step, the robber must either steal or skip. But without knowing the value of
future homes at time-step, i (ex homes i+1, i+2, … i+n), there’s no way for the robber to decide if
he should loot home i.

And this is where recursion comes in, let’s see some pseudo code!

max(
    home i + loot(home i+2), # steal from home i
         0 + loot(home i+1) # skip home i
)
"""
from functools import lru_cache


def rob1(arr: list):
    memory = {}

    def helper1(i = 0):  # base case
        if i >= len(arr):
            return 0
        if i not in memory:  # recursion
            steal = arr[i] + helper1(i + 2)
            skip = helper1(i + 1)
            memory[i] = max(steal, skip)
        return memory[i]
    return helper1()


def rob2(arr: list):
    return helper2(arr)


@lru_cache(maxsize=None)
def helper2(arr: list, i: int = 0) -> int:
    if i >= len(arr):
        return 0
    else:
        a = arr[i]
        b = helper2(arr, i+2)
        c = helper2(arr, i+1)
        return max(a + b, c)


if __name__ == '__main__':
    arr = [1, 3, 5, 7, 9, 11]
    print(f'{rob1(arr) = }')
    print(f'{rob2(arr) = }')
