import binascii
from io import BytesIO
from mimetypes import types_map
from pathlib import Path
from typing import cast, Optional, Tuple, Union

import charset_normalizer
import filetype # type: ignore[import-untyped]
from unix_perms import InvalidOctalError, from_octal_to_permissions_mode

from simple_uu.exceptions import (FileExtensionNotDetected,
                                  InvalidPermissionsMode,
                                  InvalidUUEncodingError)
from simple_uu.logger import set_up_logger
from simple_uu.types import UUEncodedFile
from simple_uu.utils import load_file_object

logger = set_up_logger(__name__)

# Maximum length of binary for a given line of uuencoded data
_MAX_BINARY_LENGTH = 45

def _permissions_mode(octal_permission: Optional[Union[str, int]]) -> str:
    """
    A private function to convert an octal into a Unix permissions mode.
    """
    if octal_permission is None:
        octal_permission = 0o644

        logger.info(
            "No permissions mode was given, mode has automatically been generated"
        )

    try:
        permissions_mode: str = from_octal_to_permissions_mode(
            octal=octal_permission
        )
    except InvalidOctalError:
        raise InvalidPermissionsMode('Permissions mode included is invalid')
    else:
        return permissions_mode


def _file_extension(extension: Optional[str]) -> Optional[str]:
    """
    A private function to validate any extension provided by user.
    """
    if extension is not None:
        if not extension.startswith('.'):
            local_extension = '.' + extension

        if local_extension not in types_map:
            raise ValueError('Invalid file extension provided')

    return extension


def _encode_from_charset_normalizer(
    content: bytes,
    encoding_validation: bool,
    binary_validation: bool
) -> Tuple[BytesIO, Optional[str], Optional[str]]:
    """
    A private function to validate that a bytes object is binary and detect mime and extension.
    Returns a tuple containing a BytesIO instance along with the detected mime type and file extension.
    """
    # Ensure that file object passed is in binary form
    if binary_validation:
        is_binary = charset_normalizer.is_binary(content)
        if not is_binary:
            raise InvalidUUEncodingError(
                "The file included is not a binary file, must be a binary file"
            )

    # Ensure that binary data does not have a character encoding
    if encoding_validation:
        encoding = charset_normalizer.from_bytes(content).best()
        if encoding is not None:
            raise InvalidUUEncodingError(
                "Binary file cannot have a character encoding"
            )

    # Detect mime type and file extension from binary
    file_mime_type_from_detection: Optional[str] = filetype.guess_mime(content)
    file_extension_from_detection: Optional[str] = filetype.guess_extension(content)

    return (
        BytesIO(content), file_mime_type_from_detection, file_extension_from_detection
    )


def encode(
    file_object: Union[str, Path, bytes, bytearray],
    filename: str,
    octal_permission: Optional[Union[str, int]] = None,
    extension: Optional[str] = None,
    encoding_validation: bool = True,
    binary_validation: bool = True
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
        filename (str): The name of the file being encoded.
        octal_permission (str | int | None): An octal permission as a string or integer.
        extension (str | None): An extension for the file being encoded.
        encoding_validation (bool): Boolean indicating whether to run encoding validation.
        binary_validation (bool): Boolean indicating whether to run binary validation.

    Returns:
        UUEncodedFile: A UUEncodedFile instance providing the encoded data along with
            a number of attributes, properties, and methods.
    """
    filename = '_'.join(item for item in filename.split())
    permissions_mode = _permissions_mode(octal_permission=octal_permission)
    file_extension = _file_extension(extension=extension)

    # Load file and collection objects
    binary_data = bytearray()
    binary_buffer, file_mime_type_from_detection, file_extension_from_detection  = _encode_from_charset_normalizer(
        content=load_file_object(file_object=file_object),
        encoding_validation=encoding_validation,
        binary_validation=binary_validation
    )

    # If no file extension was provided and there was not a successful detection
    # raise a FileExtensionNotDetected error
    if file_extension is None and file_extension_from_detection is None:
        raise FileExtensionNotDetected(
            'File extension was not provided and could not be detected from signature'
        )
    else:
        if file_extension != file_extension_from_detection:
            logger.warning(
                "The file extension generated from file type detection does not match extension provided"
            )

    # By default, use extension from detection over that provided by user
    # If file extension cannot be detected, then the extension provided  is used
    file_extension_final = cast(
        str,
        file_extension_from_detection if file_extension_from_detection is not None
        else file_extension
    )

    # Generate header for uuencoded file and add to bytearray
    full_filename: str = filename + '.' + file_extension_final
    uu_header: bytes = f'begin {permissions_mode} {full_filename}\n'.encode('ascii')
    binary_data.extend(uu_header)

    # Original length of buffer
    buffer_length = len(binary_buffer.getvalue())

    # Iterate through every 45 bits of the binary data and encode with binascii
    while binary_buffer.tell() != buffer_length:
        bytes_line: bytes = binary_buffer.read(_MAX_BINARY_LENGTH)
        encoded_bytes: bytes = binascii.b2a_uu(bytes_line)
        binary_data.extend(encoded_bytes)

    # Add footer to bytearray
    binary_data.extend(b'\nend')

    # Structure all related variables in a UUEncodedFile instance
    encoded_file = UUEncodedFile(
        filename=filename,
        permissions_mode=permissions_mode,
        file_mime_type=file_mime_type_from_detection,
        file_extension=file_extension_final
    )
    encoded_file.uu_bytes = binary_data

    return encoded_file
