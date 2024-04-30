import charset_normalizer
import chardet

from simple_uu import encode

with open('./tests/examples/encoded/example_1.txt', 'rb') as in_file:
    content = in_file.read()

example_file_object = bytearray(b'\x00\x00\x00\x08\x00\x03\x01\x12\x00\x03\x00')
encoding = charset_normalizer.from_bytes(bytes(example_file_object)).best()
print(encoding.encoding)


# encode(file_object=example_file_object, filename='example_2')