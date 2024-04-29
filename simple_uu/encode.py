import binascii
from typing import Optional, Union
from pathlib import Path
from io import BytesIO
from mimetypes import types_map

import charset_normalizer
import filetype
from unix_perms import from_octal_to_permissions_code

from simple_uu.utils import load_file_object
from simple_uu.types import UUEncodedFile
from simple_uu.logger import set_up_logger
from simple_uu.exceptions import (
    FileExtensionNotDetected,
    InvalidUUEncodingError
)

logger = set_up_logger(__name__)

# Maximum length of binary for a given line of uuencoded data
_MAX_BINARY_LENGTH = 45

def _permissions_mode(octal_permission: Optional[Union[str, int]]) -> int:
    """
    A private function to convert an octal into a Unix permissions mode.
    """
    if octal_permission is None:
        return 0o644
    else:
        return from_octal_to_permissions_code(
            octal=octal_permission
        )
    

def _file_extension(extension: Optional[str]) -> Optional[str]:
    """
    A private function to validate any extension provided by user.
    """
    if extension is not None:
        if not extension.startswith('.'):
            local_extension = '.' + extension

        if local_extension not in types_map:
            raise ValueError('invalid extension provided')
        
    return extension


def encode(
    file_object: Union[str, Path, bytes, bytearray],
    file_name: str,
    octal_permission: Optional[Union[str, int]] = None,
    extension: Optional[str] = None
) -> UUEncodedFile:
    """
    Encode binary data into a uuencoded format.

    An octal permission should be a string or an integer. If the argument is
    a string, the value must be either in the format of an octal literal (e.g., '0o777')
    or as a Unix permissions code (e.g., '777'). If the value is an integer, it must be a
    decimal representation of an octal as an octal literal (e.g., 0o777) or directly as an
    integer (e.g., 511).

    The two optional arguments are octal_permission and extension. If an octal permission
    is not provided, the default octal literal 0o644 will be used. If an extension is
    not provided the it will be detected based off of the binary data.

    Args:
        file_object (str | Path | bytes | bytearray): A file object is either a path
            to a file, bytes object or bytearray object. All must contain binary data.
        file_name (str): The name of the file being encoded.
        octal_permission (str | int | None): An octal permission as a string or integer.
        extension (str | None): An extension for the file being encoded.

    Returns:
        UUEncodedFile: A UUEncodedFile instance providing the encoded data along with
            a number of attributes, properties, and methods.
    """
    file_name = '_'.join(item for item in file_name.split())
    permissions_mode = _permissions_mode(octal_permission=octal_permission)
    file_extension = _file_extension(extension=extension)

    # Load file and collection objects
    binary_data = bytearray()
    binary_bytes: bytes = load_file_object(file_object=file_object)

    # Ensure that file object passed is in binary form
    is_binary = charset_normalizer.is_binary(binary_bytes)
    if not is_binary:
        raise InvalidUUEncodingError(
            "the file included is not a binary file, must be a binary file"
        )
    
    # Detect mime type and file extension from binary
    file_mime_type_from_detection: Optional[str] = filetype.guess_mime(binary_bytes)
    file_extension_from_detection: Optional[str] = filetype.guess_extension(binary_bytes)

    # If no file extension was provided and there was not a successful detection
    # raise a FileExtensionNotDetected error
    if file_extension is None and file_extension_from_detection is None:
        raise FileExtensionNotDetected()
    else:
        if file_extension != file_extension_from_detection:
            logger.warning(
                "the file extension generated from file type detection does not match the extension provided"
            )

    # Generate header for uuencoded file and add to bytearray
    full_filename: str = file_name + '.' + file_extension_from_detection
    uu_header: bytes = f'begin {permissions_mode} {full_filename}\n'.encode('ascii')
    binary_data.extend(uu_header)

    # Convert validated binary data into a BytesIO instance
    binary_bytes_buffer = BytesIO(initial_bytes=binary_bytes)
    buffer_length = len(binary_bytes_buffer.getvalue())

    # Iterate through every 45 bits of the binary data and encode with binascii
    while binary_bytes_buffer.tell() != buffer_length:
        bytes_line: bytes = binary_bytes_buffer.read(_MAX_BINARY_LENGTH)
        encoded_bytes: bytes = binascii.b2a_uu(bytes_line)
        binary_data.extend(encoded_bytes)

    # Structure all related variables in a UUEncodedFile instance
    encoded_file = UUEncodedFile(
        file_name=file_name,
        permissions_mode=permissions_mode,
        file_mime_type=file_mime_type_from_detection,
        file_extension=file_extension_from_detection
    )
    encoded_file.uu_decoded_bytes = binary_data

    return encoded_file