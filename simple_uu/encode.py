import binascii
from typing import Optional, Union
from pathlib import Path
from io import BytesIO
from mimetypes import types_map

import charset_normalizer
import filetype

from simple_uu.utils import load_file_object
from simple_uu.types import UUEncodedFile
from simple_uu.logger import set_up_logger
from simple_uu.exceptions import (
    FileExtensionNotDetected,
    InvalidUUEncodingError
)

logger = set_up_logger(__name__)

# maximum length of binary for a given uuencoded line
_MAX_BINARY_LENGTH = 45

def encode(
    file_object: Union[str, Path, bytes, bytearray],
    file_name: str,
    permissions_mode: Optional[str] = None,
    extension: Optional[str] = None
) -> UUEncodedFile:
    """
    """
    file_name = '_'.join(item for item in file_name.split())

    if permissions_mode is None:
        pass

    if extension is not None:
        if not extension.startswith('.'):
            local_extension = '.' + extension

        if local_extension not in types_map:
            raise ValueError('invalid extension provided')

    binary_data = bytearray()
    binary_bytes: bytes = load_file_object(file_object=file_object)

    is_binary = charset_normalizer.is_binary(binary_bytes)
    
    if not is_binary:
        raise InvalidUUEncodingError(
            "the file included is not a binary file, must be a binary file"
        )
    
    file_mime_type_from_detection: Optional[str] = filetype.guess_mime(binary_bytes)
    file_extension_from_detection: Optional[str] = filetype.guess_extension(binary_bytes)

    if extension is None and file_extension_from_detection is None:
        raise FileExtensionNotDetected()
    else:
        if extension != file_extension_from_detection:
            logger.warning(
                "the file extension generated from file type detection does not match the extension provided"
            )

    # add header to bytesarray
    full_filename: str = file_name + '.' + file_extension_from_detection
    uu_header: bytes = f'begin {permissions_mode} {full_filename}\n'.encode('ascii')
    binary_data.extend(uu_header)

    binary_bytes_buffer = BytesIO(initial_bytes=binary_bytes)
    buffer_length = len(binary_bytes_buffer.getvalue())

    while binary_bytes_buffer.tell() != buffer_length:
        bytes_line: bytes = binary_bytes_buffer.read(_MAX_BINARY_LENGTH)
        encoded_bytes: bytes = binascii.b2a_uu(bytes_line)
        binary_data.extend(encoded_bytes)

    encoded_file = UUEncodedFile(
        file_name=file_name,
        permissions_mode=permissions_mode,
        file_mime_type=file_mime_type_from_detection,
        file_extension=file_extension_from_detection
    )
    encoded_file.uu_decoded_bytes = binary_data

    return encoded_file