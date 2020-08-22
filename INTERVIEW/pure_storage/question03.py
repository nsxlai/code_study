"""
Find the list of all files in a given directory

   my_dir1
    |- file1.txt
    |- file2.txt
    |- my_dir2
        |- sfile1.txt
        |- sfile2.txt

    output = ['file1.txt', 'file2.txt', 'sfile1.txt', 'sfile2.txt']

    scratchpad output =  ['file1.txt', 'file2.txt', 'my_dir2']
"""
import os


def file_list(dir_name):
    if os.path.isdir(dir_name) is False:
        return
    f_list = []
    dir_out = os.listdir(dir_name)
    for item in dir_out:
        f_out = []
        if os.path.isdir(item):
            f_out = file_list(item)
        else:
            f_out = os.listdir(dir_name)
        f_list += f_out
    return f_list


