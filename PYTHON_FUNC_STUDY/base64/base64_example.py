"""
source: https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/

  Why use Base64 Encoding?
    In computers, all data of different types are transmitted as 1s and 0s. However, some communication
    channels and applications are not able to understand all the bits it receives. This is because the
    meaning of a sequence of 1s and 0s is dependent on the type of data it represents. For example,
    10110001 must be processed differently if it represents a letter or an image.

    To work around this limitation, you can encode your data to text, improving the chances of it being
    transmitted and processed correctly. Base64 is a popular method to get binary data into ASCII characters,
    which is widely understood by the majority of networks and applications.

    A common real-world scenario where Base64 encoding is heavily used are in mail servers. They were originally
    built to handle text data, but we also expect them to send images and other media with a message. In
    those cases, your media data would be Base64 encoded when it is being sent. It will then be Base64 decoded
    when it is received so an application can use it.
"""
import base64


def msg_encode(message: str) -> str:
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def msg_decode(base64_message: str) -> str:
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message


if __name__ == '__main__':
    original_message = "Python is fun"
    print(f'{original_message = }')

    encoded_message = msg_encode(message=original_message)
    print(f'{encoded_message = }')

    decoded_message = msg_decode(base64_message=encoded_message)
    print(f'{decoded_message = }')
