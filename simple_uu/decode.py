import binascii
from binascii import Error
from typing import Generator, Optional, Union
import os

import charset_normalizer
import filetype

from simple_uu.exceptions import InvalidUUEncodedFileError
from simple_uu.types import UUDecodedFile
from simple_uu.utils import decompose_file_name

def _from_charset_normalizer(content: bytes) -> Generator[bytes, None, None]:
    """
    """
    uu_encoded_content = charset_normalizer.from_bytes(content)
    encoding = uu_encoded_content.best()

    if encoding.encoding not in {'ascii', 'utf_8'}:
        raise InvalidUUEncodedFileError(
            "invalid uu encode file format, file does not have an ascii encoding"
        )
    
    for line in encoding.raw.split(b'\n'):
        yield line


def decode(file_object: Union[bytes, bytearray, str]) -> UUDecodedFile:
    """
    """
    binary_data = bytearray()
    end_footer_included = False
    
    # If a str is passed in, then this is expected to be an existing file path
    if isinstance(file_object, str):
        if os.path.exists(file_object):
            with open(file_object, 'rb') as uu_encoded_file:
                uu_encoded_bytes: bytes = uu_encoded_file.read()
        else:
            raise FileNotFoundError("file path passed does not reference a valid file")
    elif isinstance(file_object, bytes):
        uu_encoded_bytes: bytes = file_object
    elif isinstance(file_object, bytearray):
        uu_encoded_bytes: bytes = bytes(file_object)
    else:
        raise TypeError(
            f"{type(file_object)} is an invalid type for 'file', must be one of (bytes, bytearray, str)"
        )

    uu_encoded_content = _from_charset_normalizer(content=uu_encoded_bytes)

    # Skip any excess white space before the header, if there are issues
    while uu_encoded_content:
        header_line: bytes = next(uu_encoded_content)

        if not header_line.startswith(b'\n'):
            break

    begin, permissions_mode, file_name = header_line.split(b' ')
    
    if begin != b'begin':
        raise InvalidUUEncodedFileError(
            "invalid uu encode file format, missing 'begin' header at start of file"
        )
    
    try:
        _ = int(permissions_mode)
    except ValueError:
        raise InvalidUUEncodedFileError(
            "invalid uu encode file format, permissions code included is not valid"
        )
    else:
        assert len(permissions_mode) == 3
        
    # Extract the permissions mode of uu enecoded file
    permissions_mode_decoded: str = permissions_mode.decode()
    
    for line in uu_encoded_content:
        if line.startswith(b'\r') or line.startswith(b'\n'):
            break
        elif line.startswith(b'end'):
            end_footer_included = True
            break
        else:
            line_clean: bytes = line.rstrip(b'\n\r')
            
            try:
                decoded_output: bytes = binascii.a2b_uu(line_clean)
            except Error as exec_info:
                if 'Illegal char' in str(exec_info):
                    raise InvalidUUEncodedFileError(
                        "invalid character included in file, not a valid ascii character"
                    )
                else:
                    nbytes: int = (((line_clean[0] - 32) & 63) * 4 + 5) // 3
                    decoded_output: bytes = binascii.a2b_uu(line_clean[:nbytes])
            finally:
                binary_data.extend(decoded_output)

    # Raise error if there was nothing in the file
    if not binary_data:
        raise InvalidUUEncodedFileError("no data in file, nothing was decoded")

    # Structure all decoded uu file and characteristics
    file_name_from_uu, file_extension_from_uu = decompose_file_name(file_name_from_uu=file_name)
            
    file_mime_type_from_detection: Optional[str] = filetype.guess_mime(binary_data)
    file_extension_from_detection: Optional[str] = filetype.guess_extension(binary_data)

    if file_extension_from_uu != file_extension_from_detection:
        pass

    decoded_file = UUDecodedFile(
        file_name=file_name_from_uu,
        permissions_mode=permissions_mode_decoded,
        end_footer_included=end_footer_included,
        file_mime_type=file_mime_type_from_detection,
        file_extension=file_extension_from_detection
    )
    decoded_file._set_uu_bytearray(decoded_bytes=binary_data)
       
    return decoded_file

decoded_file = decode(file_object='C:/Users/12158/Desktop/Test UU/test_uu_simple.txt')
print(decoded_file)