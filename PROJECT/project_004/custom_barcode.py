"""
https://www.geeksforgeeks.org/how-to-generate-barcode-in-python/
https://www.scandit.com/blog/types-barcodes-choosing-right-barcode/
"""
from tkinter import *
from PIL import ImageTk, Image
from barcode import EAN13, Code39
from barcode.writer import ImageWriter
import re


def generate_svg_file(filename: str, code_str: str):
    # Create an object of EAN13
    # my_code = EAN13(code_str)
    my_code = Code39(code_str)

    # Our barcode is ready. Let's save it (generate SVG file).
    my_code.save(filename)


def generate_png_file(filename: str, code_str: str):
    # Now, let's create an object of EAN13 class and
    # pass the number with the ImageWriter() as the
    # writer
    # my_code = EAN13(code_str, writer=ImageWriter())
    my_code = Code39(code_str, writer=ImageWriter())

    # Our barcode is ready. Let's save it.
    my_code.save(filename)


def display_png_PIL(filename: str):
    """ This opens the barcode image via Windows Image program """
    img = Image.open(filename)
    img.show()


def display_png_TK(filename: str):
    root = Tk()
    canvas = Canvas(root, width=800, height=280)
    canvas.pack()
    img = ImageTk.PhotoImage(Image.open(filename))
    canvas.create_image(20, 20, anchor=NW, image=img)
    root.mainloop()


if __name__ == '__main__':
    # Make sure to pass the number as string
    # number = '5901234123457'
    input_str = '[)>RS06GSY8161302000000XGSP1X391433AGS12V000000000GST1121045151530011RSEOT'

    sn = re.search(r'GST(\w+)RSEOT', input_str)
    sn = sn.group(1)
    print(f'{sn = }')
    generate_svg_file(filename='new_code', code_str=sn)
    generate_png_file(filename='new_code', code_str=sn)
    # display_png_PIL(filename='new_code.png')
    display_png_TK(filename='new_code1.png')
