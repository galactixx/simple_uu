import pytest
from simple_uu import (
    encode,
    FileExtensionNotDetected,
    InvalidPermissionsMode,
    InvalidUUEncodingError
)


def test_encode_error_permissions_mode() -> None:
    """
    Test error handling for an invalid permissions mode.
    """
    example_file_object = bytearray(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01')
    with pytest.raises(InvalidPermissionsMode) as exc_info:
        _ = encode(
            file_object=example_file_object, filename='example', octal_permission='999'
        )
    assert str(exc_info.value) == 'permissions mode included is invalid'

    with pytest.raises(InvalidPermissionsMode) as exc_info:
        _ = encode(
            file_object=example_file_object, filename='example', octal_permission='7777'
        )
    assert str(exc_info.value) == 'permissions mode included is invalid'


def test_encode_error_file_extension() -> None:
    """
    Test error handling for an invalid file extension.
    """
    example_file_object = bytearray(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01')
    with pytest.raises(ValueError) as exc_info:
        _ = encode(
            file_object=example_file_object, filename='example', extension='fake'
        )
    assert str(exc_info.value) == 'invalid file extension provided'

    
def test_encode_error_is_binary() -> None:
    """
    Test error handling for a file that is not binary or has a character encoding.
    """
    example_file_object = bytearray(
        b'M_]C_X  02D9)1@ ! 0$ 8 !@  #_X0)F17AI9@  34T *@    @  P$2'
        b'M-7UN2"(89-ESTUAGE4R$8+04B>I\\Z=2?E\'R74)!RVX-S\'?".&A@_F%!7C@?L'
    )

    # Test for a binary file that has a character encoding
    with pytest.raises(InvalidUUEncodingError) as exc_info:
        _ = encode(
            file_object=example_file_object, filename='example', extension='jpg'
        )
    assert str(exc_info.value) == 'binary file cannot have a character encoding'

    example_file_object = bytearray(
        b'this is clearly not binary data, should throw an error'
    )

    # Test for a file that is not binary
    with pytest.raises(InvalidUUEncodingError) as exc_info:
        _ = encode(
            file_object=example_file_object, filename='example', extension='jpg'
        )
    assert str(exc_info.value) == (
        'the file included is not a binary file, must be a binary file'
    )


def test_encode_error_file_extension() -> None:
    """
    Test error handling for an unknown file extension/type.
    """
    example_file_object = bytearray(
        b'\x01\x00`\x00`\x00\x00\xff\xe1\x02fExif\x00\x00MM\x00*'
    )
    with pytest.raises(FileExtensionNotDetected) as exc_info:
        _ = encode(
            file_object=example_file_object, filename='example'
        )
    assert str(exc_info.value) == (
        'the file extension was not provided, and could not be detected from the signature'
    )


def test_encode_partial() -> None:
    """
    Testing the encode function on partial files.
    """
    # Test example 1
    example_1_bytes = bytearray(
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xe1\x02fExif\x00\x00MM\x00*'
        b'\x00\x00\x00\x08\x00\x03\x01\x12\x00\x03\x00'
    )
    example_1_encode = encode(
        file_object=example_1_bytes, filename='example_1', octal_permission='642'
    )

    assert example_1_encode.filename == 'example_1'
    assert example_1_encode.permissions_mode == '642'
    assert example_1_encode.uu_bytes == (
        bytes(
            b'begin 642 example_1.jpg\n'
            b'M_]C_X  02D9)1@ ! 0$ 8 !@  #_X0)F17AI9@  34T *@    @  P$2  , \n'
            b'\nend'
        )
    )

    # Test example 2
    example_2_bytes = bytearray(
        b'PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\xdd+\x8bXl\x01\x00\x00\x10\x05\x00'
        b'\x00\x13\x00\x08\x02[Content_Types]'
    )
    example_2_encode = encode(
        file_object=example_2_bytes, filename='example_2', octal_permission='555'
    )

    assert example_2_encode.filename == 'example_2'
    assert example_2_encode.permissions_mode == '555'
    assert example_2_encode.uu_bytes == (
        bytes(
            b'begin 555 example_2.zip\n'
            b'M4$L#!!0 !@ (    (0#=*XM8; $  ! %   3  @"6T-O;G1E;G1?5\'EP97-=\n'
            b'\nend'
        )
    )

    # Test example 3
    example_3_bytes = bytearray(
        b'5}nH"\x18d\xd9s\xd3Xg\x95L\x84`\xb4\x14\x89\xea|\xe9\xd4'
        b'\x9f\x94|\x97P\x90r\xdb\x83s\x1d\xf0\x8e\x1a\x18?\x98PW\x8e\x07\xec'
    )
    example_3_encode = encode(
        file_object=example_3_bytes, filename='example_3', octal_permission='000', extension='doc'
    )

    assert example_3_encode.filename == 'example_3'
    assert example_3_encode.permissions_mode == '000'
    assert example_3_encode.uu_bytes == (
        bytes(
            b'begin 000 example_3.doc\n'
            b'M-7UN2"(89-ESTUAGE4R$8+04B>I\\Z=2?E\'R74)!RVX-S\'?".&A@_F%!7C@?L\n'
            b'\nend'
        )
    )

    # Test example 4
    example_4_bytes = bytearray(
        b'5}nH"\x18d\xd9s\xd3Xg\x95L\x84`\xb4\x14\x89\xea|\xe9\xd4'
        b'\x9f\x94|\x97P\x90r\xdb\x83s\x1d\xf0\x8e\x1a\x18?\x98PW\x8e\x07\xec'
    )
    example_4_encode = encode(
        file_object=example_4_bytes, filename='example_3', octal_permission='000', extension='doc'
    )

    assert example_4_encode.filename == 'example_3'
    assert example_4_encode.permissions_mode == '000'
    assert example_4_encode.uu_bytes == (
        bytes(
            b'begin 000 example_3.doc\n'
            b'M-7UN2"(89-ESTUAGE4R$8+04B>I\\Z=2?E\'R74)!RVX-S\'?".&A@_F%!7C@?L\n'
            b'\nend'
        )
    )


def test_encode_complete() -> None:
    """
    Testing the encode function on complete files.
    """
    # Test example 1
    example_1_encode = encode(
        file_object='./tests/examples/decoded/example_1.jpg',
        filename='example_1',
        octal_permission='420'
    )

    with open('./tests/examples/encoded/example_1.txt', 'r', newline='') as example_file:
        example_1_encoded_test = bytes(example_file.read(), encoding='ascii')

    assert example_1_encode.file_extension == 'jpg'
    assert example_1_encode.file_mime_type == 'image/jpeg'
    assert example_1_encode.filename == 'example_1'
    assert example_1_encode.full_filename == 'example_1.jpg'
    assert example_1_encode.permissions_mode == '420'
    assert example_1_encode.uu_bytes == example_1_encoded_test

    # Test example 2
    example_2_encode = encode(
        file_object='./tests/examples/decoded/example_2.xlsx',
        filename='example_2',
        octal_permission='777'
    )

    with open('./tests/examples/encoded/example_2.txt', 'r', newline='') as example_file:
        example_2_encoded_test = bytes(example_file.read(), encoding='ascii')

    assert example_2_encode.file_extension == 'xlsx'
    assert example_2_encode.file_mime_type == (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    assert example_2_encode.filename == 'example_2'
    assert example_2_encode.full_filename == 'example_2.xlsx'
    assert example_2_encode.permissions_mode == '777'
    assert example_2_encode.uu_bytes == example_2_encoded_test

    # Test example 3
    example_3_encode = encode(
        file_object='./tests/examples/decoded/example_3.docx',
        filename='example_3',
        octal_permission='111'
    )

    with open('./tests/examples/encoded/example_3.txt', 'r', newline='') as example_file:
        example_3_encoded_test = bytes(example_file.read(), encoding='ascii')

    assert example_3_encode.file_extension == 'docx'
    assert example_3_encode.file_mime_type == (
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    assert example_3_encode.filename == 'example_3'
    assert example_3_encode.full_filename == 'example_3.docx'
    assert example_3_encode.permissions_mode == '111'
    assert example_3_encode.uu_bytes == example_3_encoded_test

    # Test example 4
    example_4_encode = encode(
        file_object='./tests/examples/decoded/example_4.pptx',
        filename='example_4',
        octal_permission='741'
    )

    with open('./tests/examples/encoded/example_4.txt', 'r', newline='') as example_file:
        example_4_encoded_test = bytes(example_file.read(), encoding='ascii')

    assert example_4_encode.file_extension == 'pptx'
    assert example_4_encode.file_mime_type == (
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )
    assert example_4_encode.filename == 'example_4'
    assert example_4_encode.full_filename == 'example_4.pptx'
    assert example_4_encode.permissions_mode == '741'
    assert example_4_encode.uu_bytes == example_4_encoded_test