# source: https://www.hackerrank.com/challenges/sock-merchant/problem?h_r=internal-search


def sockMerchant(n, ar):
    """
    Strategy: Use the first element to see if the matching element is in the rest of the array or not. If so,
              increase the pair_count by 1 and pop the first and the matching element from the array. Continue
              the loop until the end of the array.
    """
    i = 0
    pair_count = 0
    while i < n:
        try:
            print(f'ar = {ar}')
            if ar[0] in ar[1:]:
                pop_idx = ar[1:].index(ar[0])
                print(f'pop_idx = {pop_idx + 1}')
                print(f'popping {ar.pop(0)}')
                print(f'popping {ar.pop(pop_idx)}')
                pair_count += 1
                # print(f'ar modified = {ar}')
            else:
                print(f'no pair found; popping {ar.pop(0)}')
            i += 1
            print('-' * 40)
        except IndexError:
            print('end of process')
            return pair_count
    return pair_count


if __name__ == '__main__':
    ar1 = [10, 20, 20, 10, 10, 30, 50, 10, 20]
    n1 = 9
    pair_count = sockMerchant(n1, ar1)
    print(f'pair_count1 = {pair_count}')

    print('-' * 45)
    ar2 = [1, 1, 3, 1, 2, 1, 3, 3, 3, 3]
    n2 = 10
    pair_count = sockMerchant(n2, ar2)
    print(f'pair_count2 = {pair_count}')