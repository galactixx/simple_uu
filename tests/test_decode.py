import pytest

from simple_uu import decode

def test_decode_partial() -> None:
    """
    Testing the decode function on partial files.
    """
    # Test example 1
    example_1_bytes = bytearray(
        b'begin 777 example_1.jpg\n'
        b'M_]C_X  02D9)1@ ! 0$ 8 !@  #_X0)F17AI9@  34T *@    @  P$2  , \n'
        b'\nend'
    )
    example_1_decode = decode(file_object=example_1_bytes)

    assert example_1_decode.end_footer_included
    assert example_1_decode.filename == 'example_1'
    assert example_1_decode.permissions_mode == '777'
    assert example_1_decode.uu_bytes == (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xe1\x02fExif\x00\x00MM\x00*'
        b'\x00\x00\x00\x08\x00\x03\x01\x12\x00\x03\x00'
    )

    # Test example 2
    example_2_bytes = bytearray(
        b'begin 634 example_2.xls\n'
        b'M4$L#!!0 !@ (    (0#=*XM8; $  ! %   3  @"6T-O;G1E;G1?5\'EP97-=\n'
        b'\nend'
    )
    example_2_decode = decode(file_object=example_2_bytes)

    assert example_2_decode.end_footer_included
    assert example_2_decode.filename == 'example_2'
    assert example_2_decode.permissions_mode == '634'
    assert example_2_decode.uu_bytes == (
        b'PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\xdd+\x8bXl\x01\x00\x00\x10\x05\x00'
        b'\x00\x13\x00\x08\x02[Content_Types]'
    )

    # Test example 3
    example_3_bytes = bytearray(
        b'begin 421 example_3.docx\n'
        b'M-7UN2"(89-ESTUAGE4R$8+04B>I\\Z=2?E\'R74)!RVX-S\'?".&A@_F%!7C@?L\n'
        b'\nend'
    )
    example_3_decode = decode(file_object=example_3_bytes)

    assert example_3_decode.end_footer_included
    assert example_3_decode.filename == 'example_3'
    assert example_3_decode.permissions_mode == '421'
    assert example_3_decode.uu_bytes == (
        b'5}nH"\x18d\xd9s\xd3Xg\x95L\x84`\xb4\x14\x89\xea|\xe9\xd4'
        b'\x9f\x94|\x97P\x90r\xdb\x83s\x1d\xf0\x8e\x1a\x18?\x98PW\x8e\x07\xec'
    )

    # Test example 4
    example_4_bytes = bytearray(
        b'begin 444 example_4.pptx\n'
        b'M99ICAUS;"TQ84R&)K"^0Z][P=1H>@==EQKVR&+.HUHYJ Q9U::Z_V6D%JNKW\n'
    )
    example_4_decode = decode(file_object=example_4_bytes)

    assert not example_4_decode.end_footer_included
    assert example_4_decode.filename == 'example_4'
    assert example_4_decode.permissions_mode == '444'
    assert example_4_decode.uu_bytes == (
        b'e\x9ac\x87\\\xdb\x0bLXS!\x89\xac/\x90\xeb\xde\xf0u\x1a\x1e\x81\xd7e\xc6\xbd\xb2\x18'
        b'\xb3\xa8\xd6\x8ej\x03\x16ui\xae\xbf\xd9i\x05\xaa\xea\xf7'
    )



def test_decode_complete() -> None:
    """
    Testing the decode function on complete files.
    """
    # Test example 1
    example_1_decode = decode(
        file_object='./tests/examples/encoded/example_1.txt'
    )

    with open('./tests/examples/decoded/example_1.jpg', 'rb') as example_file:
        example_1_decoded_test = example_file.read()

    assert example_1_decode.end_footer_included
    assert example_1_decode.file_extension == 'jpg'
    assert example_1_decode.file_mime_type == 'image/jpeg'
    assert example_1_decode.filename == 'example_1'
    assert example_1_decode.full_filename == 'example_1.jpg'
    assert example_1_decode.permissions_mode == '420'
    assert example_1_decode.uu_bytes == example_1_decoded_test

    # Test example 2
    example_2_decode = decode(
        file_object='./tests/examples/encoded/example_2.txt'
    )

    with open('./tests/examples/decoded/example_2.xlsx', 'rb') as example_file:
        example_2_decoded_test = example_file.read()

    assert example_2_decode.end_footer_included
    assert example_2_decode.file_extension == 'xlsx'
    assert example_2_decode.file_mime_type == (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    assert example_2_decode.filename == 'example_2'
    assert example_2_decode.full_filename == 'example_2.xlsx'
    assert example_2_decode.permissions_mode == '777'
    assert example_2_decode.uu_bytes == example_2_decoded_test

    # Test example 3
    example_3_decode = decode(
        file_object='./tests/examples/encoded/example_3.txt'
    )

    with open('./tests/examples/decoded/example_3.docx', 'rb') as example_file:
        example_3_decoded_test = example_file.read()

    assert example_3_decode.end_footer_included
    assert example_3_decode.file_extension == 'docx'
    assert example_3_decode.file_mime_type == (
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    assert example_3_decode.filename == 'example_3'
    assert example_3_decode.full_filename == 'example_3.docx'
    assert example_3_decode.permissions_mode == '111'
    assert example_3_decode.uu_bytes == example_3_decoded_test

    # Test example 4
    example_4_decode = decode(
        file_object='./tests/examples/encoded/example_4.txt'
    )

    with open('./tests/examples/decoded/example_4.pptx', 'rb') as example_file:
        example_4_decoded_test = example_file.read()

    assert example_4_decode.end_footer_included
    assert example_4_decode.file_extension == 'pptx'
    assert example_4_decode.file_mime_type == (
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )
    assert example_4_decode.filename == 'example_4'
    assert example_4_decode.full_filename == 'example_4.pptx'
    assert example_4_decode.permissions_mode == '741'
    assert example_4_decode.uu_bytes == example_4_decoded_test