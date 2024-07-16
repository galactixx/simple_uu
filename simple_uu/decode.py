import binascii
from binascii import Error
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import charset_normalizer
import filetype
from unix_perms import InvalidOctalError, from_octal_to_permissions_mode

from simple_uu.exceptions import (FileExtensionNotFoundError,
                                  InvalidPermissionsMode,
                                  InvalidUUDecodingError)
from simple_uu.logger import set_up_logger
from simple_uu.types import UUDecodedFile
from simple_uu.utils import (construct_filename, decompose_filename,
                             load_file_object, parse_header)

logger = set_up_logger(__name__)

# Maximum line length, including the length character
_MAX_LINE_LENGTH = 61

def _decode_from_charset_normalizer(content: bytes, encoding_validation: bool) -> BytesIO:
    """
    A private function to validate that a bytes object has an ascii encoding.
    Returns a BytesIO instance.
    """
    if encoding_validation:
        uu_encoded_content = charset_normalizer.from_bytes(content)
        encoding = uu_encoded_content.best()

        # charset_normalizer can classify uuencoded characters as utf_8, so
        # Check for both ascii and utf_8 encoding output
        if encoding is None or (
            encoding is not None and encoding.encoding not in {'ascii', 'utf_8'}
        ):
            raise InvalidUUDecodingError(
                "Invalid character encoding, file must have an ascii character encoding"
            )

    return BytesIO(initial_bytes=content)


def decode(
    file_object: Union[str, Path, bytes, bytearray],
    encoding_validation: bool = True
) -> UUDecodedFile:
    """
    Decode a file from a uuencoded format.

    Args:
        file_object (str | Path | bytes | bytearray): A file object is either a path
            to a file, bytes or bytearray object. All must contain uuencoded data.
        encoding_validation (bool): Boolean indicating whether to run encoding validation.

    Returns:
        UUDecodedFile: A UUDecodedFile instance providing the decoded data along with
            a number of attributes, properties, and methods.
    """
    binary_data = bytearray()

    # Load file object into a BytesIO instance
    uu_encoded_buffer: BytesIO = _decode_from_charset_normalizer(
        content=load_file_object(file_object=file_object),
        encoding_validation=encoding_validation
    )
    buffer_length = len(uu_encoded_buffer.getvalue())

    # In case there are any issues, any excess white space before the header is skipped
    for line in uu_encoded_buffer:
        header_line: bytes = line.strip(b'\n\r')

        if header_line:
            break

    if uu_encoded_buffer.tell() == buffer_length:
        raise InvalidUUDecodingError("There is no content in file, nothing was decoded")

    # Parse header to extract all three key items
    # (begin clause, permissions mode, and file name)
    begin, permissions_mode_uu, filename_uu = parse_header(header=header_line)

    # The header must start with 'begin' in order to move on with decoding
    if begin != b'begin':
        raise InvalidUUDecodingError("Missing 'begin' section of header at start of file")

    # Confirm the permissions mode included is valid
    try:
        # If no permissions was found in header, then set default
        if permissions_mode_uu is None:
            permissions_mode_uu = 0o644

            logger.info(
                "no permissions mode was detected in header, mode has automatically been generated"
            )
        else:
            permissions_mode_uu = permissions_mode_uu.decode('ascii')

        permissions_mode: str = from_octal_to_permissions_mode(octal=permissions_mode_uu)
    except InvalidOctalError:
        raise InvalidPermissionsMode('Permissions mode included is invalid')

    # Iterate through each line of buffer and decode using binascii
    for line in uu_encoded_buffer:
        # Perform removal of new line and carriage return characters from the end of each line
        uuencoded_line: bytes = line.rstrip(b'\n\r')

        if uuencoded_line and not uuencoded_line.startswith(b'end'):
            line_length: int = len(uuencoded_line)

            # Raise an error if the length of a line is larger than the maximum allowed
            if line_length > _MAX_LINE_LENGTH:
                raise InvalidUUDecodingError(
                    f"Length of {line_length} is larger than the maximum allowed for a line of uuencoded data"
                )

            # Run decoding from binascii
            try:
                decoded_output: bytes = binascii.a2b_uu(uuencoded_line)
            except Error:
                try:
                    # Taken from uu standard library
                    nbytes: int = (((uuencoded_line[0] - 32) & 63) * 4 + 5) // 3
                    decoded_output: bytes = binascii.a2b_uu(uuencoded_line[:nbytes])
                except Error as exc_info:
                    if str(exc_info) == 'Illegal char':
                        raise InvalidUUDecodingError(
                            "Invalid ascii character, characters should have ascii codes ranging from 32 to 96"
                        )
                    else:
                        raise Error(exc_info)
            binary_data.extend(decoded_output)

    # Raise error if there was nothing was decoded
    if not binary_data:
        raise InvalidUUDecodingError(
            "Apart from header there is no content in file, nothing was decoded"
        )

    # Extract name and extension from filename
    filename_from_uu, file_extension_from_uu = decompose_filename(filename_from_uu=filename_uu)

    # Detect mime type and file extension from binary
    file_mime_type_from_detection: Optional[str] = filetype.guess_mime(binary_data)
    file_extension_from_detection: Optional[str] = filetype.guess_extension(binary_data)

    if file_extension_from_uu != file_extension_from_detection:
        logger.warning(
            "the file extension from file type detection does not match the extension from uu header"
        )

    # By default, use extension from detection over that included in header
    # If file extension cannot be detected, then the extension provided in uu header is used
    file_extension: Optional[str] = (
        file_extension_from_detection if file_extension_from_detection is not None else file_extension_from_uu
    )
    if file_extension is None:
        raise FileExtensionNotFoundError(
            'File extension was not found in header and could not be detected from signature'
        )

    filename: str = construct_filename(filename_from_uu=filename_from_uu)

    # Structure all related variables in a UUDecodedFile instance
    decoded_file = UUDecodedFile(
        filename=filename,
        permissions_mode=permissions_mode,
        file_mime_type=file_mime_type_from_detection,
        file_extension=file_extension
    )
    decoded_file.uu_bytes = binary_data

    return decoded_file
