import binascii
from binascii import Error
from typing import Optional, Union
from pathlib import Path
from io import BytesIO

import charset_normalizer
import filetype

from simple_uu.logger import set_up_logger
from simple_uu.types import UUDecodedFile
from simple_uu.utils import (
    construct_filename,
    decompose_file_name,
    load_file_object,
    parse_header
)
from simple_uu.exceptions import (
    FileExtensionNotFoundError,
    InvalidUUDecodingError
)

logger = set_up_logger(__name__)

# Maximum line length, including the length character
_MAX_LINE_LENGTH = 61

def _from_charset_normalizer(content: bytes) -> BytesIO:
    """
    A private function to validate a bytes object has an ascii encoding and return
    a BytesIO instance.
    """
    uu_encoded_content = charset_normalizer.from_bytes(content)
    encoding = uu_encoded_content.best()

    # charset_normalizer will classify the uuencoded ascii text as utf_8, so
    # Check for both ascii and utf_8 encoding output
    if encoding.encoding not in {'ascii', 'utf_8'}:
        raise InvalidUUDecodingError(
            "invalid uu encode file format, file does not have an ascii encoding"
        )
    
    return BytesIO(initial_bytes=encoding.raw)


def decode(file_object: Union[str, Path, bytes, bytearray]) -> UUDecodedFile:
    """
    Decode a file encoded in a uuencoded format.
    
    Args:
        file_object (str | Path | bytes | bytearray): A file object is either a path
            to a file, bytes object or bytearray object. All must contain uuencoded data.

    Returns:
        UUDecodedFile: A UUDecodedFile instance providing the decoded data along with
            a number of attributes, properties, and methods.
    """
    binary_data = bytearray()
    end_footer_included = False
    
    # If a str is passed in, then this is expected to be an existing file path
    uu_encoded_bytes: bytes = load_file_object(file_object=file_object)
    uu_encoded_buffer: BytesIO = _from_charset_normalizer(content=uu_encoded_bytes)
    buffer_length = len(uu_encoded_buffer.getvalue())

    # Skip any excess white space before the header, if there are issues
    while uu_encoded_buffer.tell() != buffer_length:
        header_line: bytes = uu_encoded_buffer.readline().rstrip(b'\n\r')

        if header_line.startswith(b'\n') or header_line:
            break

    if uu_encoded_buffer.tell() == buffer_length:
        raise InvalidUUDecodingError("file is empty with no content")

    begin, permissions_mode, file_name = parse_header(header=header_line)
    
    if begin != b'begin':
        raise InvalidUUDecodingError("missing 'begin' header at start of file")
    
    try:
        _ = int(permissions_mode)
    except ValueError:
        raise InvalidUUDecodingError(
            "permissions code included is invalid or could not be found"
        )
    else:
        assert len(permissions_mode) == 3
        
    # Extract the permissions mode of uu enecoded file
    permissions_mode_decoded: str = permissions_mode.decode('ascii')
    
    for line in uu_encoded_buffer.readlines():
        if line.startswith(b'\r') or line.startswith(b'\n'):
            break
        elif line.startswith(b'end'):
            end_footer_included = True
            break
        else:
            line_clean: bytes = line.rstrip(b'\n\r')
            line_length: int = len(line_clean)
            if line_length > _MAX_LINE_LENGTH:
                raise InvalidUUDecodingError(
                    f"line length of {line_length} is more than the maximum allowed from a uu encoded file"
                )
            
            try:
                decoded_output: bytes = binascii.a2b_uu(line_clean)
            except Error as exec_info:
                if 'Illegal char' in str(exec_info):
                    raise InvalidUUDecodingError(
                        "invalid ascii character included in file, characters can only be between ascii codes of 32 and 96"
                    )
                else:
                    nbytes: int = (((line_clean[0] - 32) & 63) * 4 + 5) // 3
                    decoded_output: bytes = binascii.a2b_uu(line_clean[:nbytes])
            finally:
                binary_data.extend(decoded_output)

    # Raise error if there was nothing in the file
    if not binary_data:
        raise InvalidUUDecodingError("no data in file, nothing was decoded")

    # Structure all decoded uu file and characteristics
    file_name_from_uu, file_extension_from_uu = decompose_file_name(file_name_from_uu=file_name)

    file_mime_type_from_detection: Optional[str] = filetype.guess_mime(binary_data)
    file_extension_from_detection: Optional[str] = filetype.guess_extension(binary_data)

    if file_extension_from_uu != file_extension_from_detection:
        logger.warning(
            "the file extension generated from file type detection does not match the extension from uu header"
        )

    # Overwrite file extension and filename from detection, if either are None, with the file extension from uu
    file_extension: Optional[str] = (
        file_extension_from_detection if file_extension_from_detection is not None else file_extension_from_uu
    )
    if file_extension is None:
        raise FileExtensionNotFoundError()

    file_name: str = construct_filename(file_name_from_uu=file_name_from_uu)

    decoded_file = UUDecodedFile(
        file_name=file_name,
        permissions_mode=permissions_mode_decoded,
        end_footer_included=end_footer_included,
        file_mime_type=file_mime_type_from_detection,
        file_extension=file_extension
    )
    decoded_file.uu_decoded_bytes = binary_data
       
    return decoded_file