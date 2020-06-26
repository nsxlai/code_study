"""
Emma is playing a new mobile game that starts with consecutively numbered clouds.
Some of the clouds are thunderheads and others are cumulus.
She can jump on any cumulus cloud having a number that is equal to the number of the current cloud plus 1 or 2.
She must avoid the thunderheads. Determine the minimum number of jumps it will take Emma to jump from her starting
position to the last cloud. It is always possible to win the game.

For each game, Emma will get an array of clouds numbered 0 if they are safe or 1 if they must be avoided. For example,
c = [0, 1, 0, 0, 0, 1, 0] indexed from 0 - 6. The number on each cloud is its index in the list so she must avoid the
clouds at indexes 1 and 5. She could follow the following two paths: 0-> 2 -> 4 -> 6 or 0 -> 2 -> 3 -> 4 -> 6.
The first path takes 3 jumps while the second takes 4.
"""


# Complete the jumpingOnClouds function below.
def jumpingOnClouds(c):
    jump = 0
    cloud_zero_cnt = 0
    for i in range(len(c)):
        if i == 0:
            cloud_zero_cnt += 1
            continue
        print('i = {}'.format(i))
        if c[i] == 0:
            cloud_zero_cnt += 1
            if cloud_zero_cnt <= 2:
                jump += 1
                print('jump = {}'.format(jump))
                print('cloud_zero_cnt = {}'.format(cloud_zero_cnt))
            else:
                cloud_zero_cnt = 0
        else:
            cloud_zero_cnt = 0
        print('-' * 10)
    return jump


def jumpingOnClouds2(c):
    '''
    Break down the jumping points ('0') with non-jumping points ('1') with '1' as delimiter separate the elements
    The final jumps will be the jumps within each elements plus the jumps between each elements
    for example, 00100000100 will be:
    ['00', '00000', '00']
    First element has 1 jump, second element has 2 jumps, and third element has 1 jump (5 jumps total). There are 3
    elements, so 2 extra jumps will be added to the final jump (5 + 2 = 7)
    :param c:
    :return:
    '''
    temp = ''.join(map(str, c))
    temp = temp.split('1')
    # print(temp)
    jump = 0
    for i in temp:  # calculate jumps within each element
        num = len(i) // 2
        jump = jump + num
    jump = jump + (len(temp) - 1)  # calculate jumps between each element
    return jump


if __name__ == '__main__':
    test_case1 = '0 0 1 0 0 0 0 1 0'
    test_case1 = [int(i) for i in test_case1.split()]
    test_case2 = '0 0 1 0 0 0 0 1 0 0 0 0 1 0'
    test_case2 = [int(i) for i in test_case2.split()]
    test_case3 = '0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 1 0'
    test_case3 = [int(i) for i in test_case3.split()]
    test_case = '0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 1 0 1 0 0 0 1 0 0 1 0 0 0 1 0 1 0 0 0 0 0 0 0 0 1 0 0 1 0 1 0 0'
    test_case = [int(i) for i in test_case.split()]

    # result = jumpingOnClouds(test_case1)
    # print(f'number of jumps = {result}')
    # assert result == 5
    #
    # result = jumpingOnClouds(test_case2)
    # print(f'number of jumps = {result}')
    # assert result == 8
    #
    # result = jumpingOnClouds(test_case3)
    # print(f'number of jumps = {result}')
    # assert result == 11

    print(jumpingOnClouds2(test_case1))
    print(jumpingOnClouds2(test_case2))
    print(jumpingOnClouds2(test_case3))
    print(jumpingOnClouds2(test_case))