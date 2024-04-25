from typing import Optional, Tuple, Union
import os
import uuid
from pathlib import Path

from simple_uu.logger import set_up_logger

logger = set_up_logger(__name__)

def load_file_object(file_object: Union[str, Path, bytes, bytearray]) -> bytes:
    """
    """
    if isinstance(file_object, (str, Path)):
        if os.path.exists(file_object) and os.path.isfile(file_object):
            with open(file_object, 'rb') as uu_encoded_file:
                uu_encoded_bytes: bytes = uu_encoded_file.read()
                return uu_encoded_bytes
        else:
            raise FileNotFoundError("file path passed does not reference a valid file")
    elif isinstance(file_object, bytes):
        uu_encoded_bytes: bytes = file_object
        return uu_encoded_bytes
    elif isinstance(file_object, bytearray):
        uu_encoded_bytes: bytes = bytes(file_object)
        return uu_encoded_bytes
    else:
        raise TypeError(
            f"{type(file_object)} is an invalid type for 'file', must be one of (str, Path, bytes, bytearray)"
        )


def construct_filename(file_name_from_uu: Optional[str]) -> str:
    if file_name_from_uu is None:
        uu_8_file_id = str(uuid.uuid4())[:8]
        file_name_generated = f'simple-uu-decode-{uu_8_file_id}'

        logger.info(
            f"filename did not appear in the uu header, generating alternate filename {file_name_generated}"
        )
        return file_name_generated
    else:
        return file_name_from_uu


def decompose_file_name(
    file_name_from_uu: Optional[Union[str, bytes]]
) -> Tuple[Optional[str], Optional[str]]:
    """
    """
    if file_name_from_uu is None:
        return None, None

    if isinstance(file_name_from_uu, bytes):
        file_name_from_uu = file_name_from_uu.decode('ascii')

    file_name, file_extension = os.path.splitext(file_name_from_uu)
    if not file_extension.startswith('.'):
        return file_name, None
    else:
        file_extension = file_extension.lstrip('.')
        return file_name, file_extension
    

def parse_header(header: bytes) -> Tuple[
    Optional[bytes], Optional[bytes], Optional[bytes]
]:
    """
    """
    header_items = header.split(b' ')

    # Filter out any random empty spaces
    header_items = [item.strip() for item in header_items if item.strip()]

    # Validation here in case of malformed header
    if len(header_items) == 1:

        # If there is only one header item, prioritize begin
        begin = header_items[0]
        return begin, None, None
    elif len(header_items) == 2:

        # If there is only two header items, prioritize begin and permissions
        begin = header_items[0]
        permissions_mode = header_items[1]
        return begin, permissions_mode, None
    elif len(header_items) == 3:

         # If there are three, return all
        begin = header_items[0]
        permissions_mode = header_items[1]
        file_name = header_items[2]
        return begin, permissions_mode, file_name
    else:

        # If the length of headers is more than 3, the assumption is that
        # there are spaces in the filename
        begin = header_items[0]
        permissions_mode = header_items[1]
        file_name = b' '.join(header_items[2:])

        return begin, permissions_mode, file_name