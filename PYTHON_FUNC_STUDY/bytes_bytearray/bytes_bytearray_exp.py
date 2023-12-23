"""
source:
https://www.geeksforgeeks.org/python-convert-string-to-bytes/
https://www.geeksforgeeks.org/working-with-binary-data-in-python/

"""

if __name__ == '__main__':
    test_str = 'this is a test'
    print(f'{test_str = }')

    byte_str1 = bytes(test_str, 'utf-8')
    print(f'{byte_str1 = }')
    print(f'{type(byte_str1) = }')

    # Alternatively
    byte_str2 = test_str.encode('utf-8')
    print(f'{byte_str2 = }')
    print(f'{type(byte_str2) = }')

    # byte string
    byte_str3 = b'\xC2\xA9\x20\xF0\x9D\x8C\x86\x20\xE2\x98\x83'
    print(f'{byte_str3 = }')
    print(f'{byte_str3.decode("utf-8")}')
    print(f'{byte_str3.decode("latin-1")}')

    # bytearray
    bytesArr1 = bytearray(b'\x00\x0F')
    bytesArr1[0] = 255  # Bytearray allows modification
    bytesArr1.append(255)
    print(f'{bytesArr1 = }')

    # Create bytearray
    byte_list = ['ff', '01', '33', '45', '65', '20', '55']
    print(f'{byte_list = }')
    bytesArr2 = bytearray()
    for i in byte_list:
        bytesArr2.append(int(i, 16))

    print(f'{bytesArr2 = }')
    print(f'{hex(bytesArr2[0]) = }')
    print(f'{hex(bytesArr2[1]) = }')
    print(f'{hex(bytesArr2[2]) = }')
    print(f'{hex(bytesArr2[3]) = }')
    print(f'{hex(bytesArr2[4]) = }')
    print(f'{hex(bytesArr2[5]) = }')
    print(f'{hex(bytesArr2[6]) = }')

    # Alternatively
    with open('testfile.bin', "wb") as file:
        binary_data = bytearray([0xFF, 0x00, 0x7F, 0x80])
        # Example binary data as a bytearray
        file.write(binary_data)

    """
    import binascii
 
    # initializing string
    test_string = "4766472069732062657374"
     
    # printing original string
    print("The original string : " + str(test_string))
     
    # Using binascii.unhexlify()
    # convert string to byte
    res = binascii.unhexlify(test_string)
     
    # print result
    print("The byte converted string is : " + str(res) + ", type : " + str(type(res)))
    
    ==========================
    # JPEG signature example
    jpeg_signatures = [ 
        binascii.unhexlify(b'FFD8FFD8'), 
        binascii.unhexlify(b'FFD8FFE0'), 
        binascii.unhexlify(b'FFD8FFE1') 
    ] 
      
    with open('food.jpeg', 'rb') as file: 
        first_four_bytes = file.read(4) 
      
        if first_four_bytes in jpeg_signatures: 
            print("JPEG detected.") 
        else: 
            print("File does not look like a JPEG.")
    """
