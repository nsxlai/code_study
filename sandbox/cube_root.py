def cube_root(n):
    """n is the input that is already cubed
       for example, if n = 27, cube_root(27) should return 3

       this is a horrible example and I have created during the Google interview. The finished part of this
       function is now at 'google_interview' folder
    """
    # determine the whole number for the cube root of n
    def cube(i):
        return i * i * i

    def cube_approx(i):
        while cube(i) < n:
            i += 1
        return i  # return the lower bound
    i = 0
    i = cube_approx(i)
    print(f'i = {i}')
    # start the approximation
    while cube(i) < n:
        i = float(i) + 0.01

    return float(i)


if __name__ == '__main__':
    for i in range(50):
        print(f'n = {i}, cube_root = {cube_root(i)}')