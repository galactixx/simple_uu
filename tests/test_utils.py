from simple_uu.utils import (
    construct_filename,
    decompose_filename,
    parse_header
)


def test_construct_filename() -> None:
    """
    Test construct filename function.
    """
    assert construct_filename(filename_from_uu='example_1') == 'example_1'
    assert construct_filename(filename_from_uu=None).startswith('simple-uu-decode')


def test_decompose_filename() -> None:
    """
    Test decompose filename function
    """
    assert decompose_filename(filename_from_uu=b'example_1.jpg') == ('example_1', 'jpg')
    assert decompose_filename(filename_from_uu=b'example_1.xlsx') == ('example_1', 'xlsx')
    assert decompose_filename(filename_from_uu=b'example 1.docx') == ('example 1', 'docx')
    assert decompose_filename(filename_from_uu=b'example 1.pptx') == ('example 1', 'pptx')
    assert decompose_filename(filename_from_uu=None) == (None, None)
    assert decompose_filename(filename_from_uu=b'example_1') == ('example_1', None)


def test_parse_header() -> None:
    """
    Test parse header function
    """
    assert parse_header(header=b'begin 777 example.jpg') == (b'begin', b'777', b'example.jpg')
    assert parse_header(header=b'begin 777') == (b'begin', b'777', None)
    assert parse_header(header=b'begin') == (b'begin', None, None)
    assert parse_header(header=b'begin 642 not so cool example.xlsx') == (
        b'begin', b'642', b'not so cool example.xlsx'
    )
    assert parse_header(header=b'begin 777 really cool example.docx') == (
        b'begin', b'777', b'really cool example.docx'
    )