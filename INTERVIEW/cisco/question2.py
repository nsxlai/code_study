"""
Write a function that takes in the ip, the octet positions represented by an array / tuple
with on and off values of 1 and 0 where 1 is on and 0 is off, and the offset to add to each
octet.

Constraints: Negative values are taken into account, cannot go over 255(256 loops back
to 0) or below 0, and must be positive.

E.g.
def change_ip(ip, octets, offset):
    # insert code here

change_ip('10.1.1.1', (1, 0, 1, 0), 10) -> 20.1.11.1
"""


def change_ip(ip, octets, offset):
    """function that takes in the ip, the octet positions represented by an array/tuple with on and off values of 1 and 0
       where 1 is on and 0 is off, and the offset to add to each octet.

       Constraints: Negative values are taken into account, cannot go over 255 (256 loops back to 0) or below 0, and must be positive.
    """
    temp_ip = ip.split('.')
    new_octets = []
    for ip, mask in zip(temp_ip, octets):
        # print('ip, mask = {} {}'.format(ip, mask))
        if mask == 1:
            temp_val = int(ip) + offset
            if temp_val >= 256:
                temp_val %= 256
            new_octets.append(temp_val)
        else:
            new_octets.append(int(ip))
        # print(new_octets)
    new_octets = '.'.join([str(x) for x in new_octets])
    return new_octets


if __name__ == '__main__':
    print('Original IP address: 10.1.1.1')
    print('New IP address: {}'.format(change_ip('10.1.1.1', (1, 0, 1, 0), 10)))
    print('-' * 20)
    print('Original IP address: 10.1.1.1')
    print('New IP address: {}'.format(change_ip('10.1.1.1', (1, 0, 1, 0), 300)))
