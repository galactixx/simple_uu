from typing import Optional, Tuple, Union
import os
from os import PathLike
import uuid

from simple_uu.logger import set_up_logger

logger = set_up_logger(__name__)

def load_file_object(file_object: Union[str, PathLike, bytes, bytearray]) -> bytes:
    """
    Loads a file object and return a bytes instance.

    Args:
        file_object (str | PathLike | bytes | bytearray): A file object is either a path
            to a file, bytes or bytearray object. All must contain uuencoded data.

    Returns:
        bytes: A bytes instance.
    """
    if not isinstance(file_object, (str, PathLike, bytes, bytearray)):
        raise TypeError(
            f"{type(file_object)} is an invalid type, must be one of (str, PathLike, bytes, bytearray)"
        )

    if isinstance(file_object, bytes):
         uu_encoded_bytes: bytes = file_object
    elif isinstance(file_object, bytearray):
         uu_encoded_bytes: bytes = bytes(file_object)
    else:
        if os.path.isfile(file_object):
            with open(file_object, 'rb') as uu_encoded_file:
                uu_encoded_bytes: bytes = uu_encoded_file.read()
        else:
            raise FileNotFoundError("file path is not valid")

    return uu_encoded_bytes


def construct_filename(filename_from_uu: Optional[str]) -> str:
    """
    Constructs a filename based on filename included in header. If a filename could not
    be found in header, then one is automatically generated, otherwise the filename
    that was found is returned.

    Args:
        filename_from_uu (str | None): Filename extracted from uu header.

    Returns:
        str: A filename attributed to the uuencoded data.
    """
    if filename_from_uu is None:
        uu_8_file_id = str(uuid.uuid4())[:8]
        file_name_generated = f'simple-uu-decode-{uu_8_file_id}'

        logger.info(
            f"filename did not appear in the uu header, auto-generating filename {file_name_generated}"
        )
        return file_name_generated
    else:
        return filename_from_uu


def decompose_filename(
    filename_from_uu: Optional[Union[str, bytes]]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts both the filename and file extension from the filename included in the
    header of the uu file.
    
    Args:
        filename_from_uu (str | None): Filename extracted from uu header.

    Returns:
        Tuple[str | None, str | None]: A tuple object containing the filename and file extension.
    """
    if filename_from_uu is None:
        return None, None

    if isinstance(filename_from_uu, bytes):
        filename_from_uu: str = filename_from_uu.decode('ascii')

    filename, file_extension = os.path.splitext(filename_from_uu)
    if not file_extension.startswith('.'):
        return filename, None
    else:
        file_extension = file_extension.lstrip('.')
        return filename, file_extension
    

def parse_header(header: bytes) -> Tuple[
    Optional[bytes], Optional[bytes], Optional[bytes]
]:
    """
    Parse header from uuencoded data into a begin clause, permissions mode, and file name.

    Validation is included in case the header is malformed. If there is only one item found in the header line,
    it is assumed that it is the begin clause. If there are two items, the begin clause and permissions
    mode are priortized. With three items we return all. Finally, if there are more than three,
    all from three onwards are assumed to be part of the filename.
    
    Args:
        header (bytes): Header line from uuencoded data.

    Returns:
        Tuple[bytes | None, bytes | None, bytes | None]: The extracted begin clause,
            permissions mode, and file name.
    """
    # Split on space and strip out any excess white space
    header_items = header.split(b' ')
    header_items = [item.strip() for item in header_items if item.strip()]
    num_header_items = len(header_items)

    # Validation in case of malformed header
    if num_header_items == 1:
        # If there is only one header item, prioritize begin
        return header_items[0], None, None
    elif num_header_items == 2:
        # If there is only two header items, prioritize begin and permissions
        return header_items[0], header_items[1], None
    elif num_header_items == 3:
        return header_items[0], header_items[1], header_items[2]
    else:
        # If the length of headers is more than 3, the assumption is that
        # there are spaces in the filename
        return (
            header_items[0], header_items[1], b' '.join(header_items[2:])
        )