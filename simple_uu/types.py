from pathlib import Path
from typing import Union
from os import PathLike

from textwrap import dedent

class BaseUUFile(object):
    """
    """
    def __init__(
        self,
        file_name: str,
        permissions_mode: str,
        file_mime_type: str,
        file_extension: str
    ):
        self.file_name = file_name
        self.permissions_mode = permissions_mode
        self.file_mime_type = file_mime_type
        self.file_extension = file_extension

        self.__bytearray: bytearray = bytearray()

    @property
    def full_filename(self) -> str:
        return f'{self.file_name}.{self.file_extension}'

    @property
    def uu_decoded_bytes(self) -> bytes:
        return bytes(self.__bytearray)

    @uu_decoded_bytes.setter
    def uu_decoded_bytes(self, decoded_bytes: bytearray) -> None:
        self.__bytearray = decoded_bytes

    def write_file(self, path: Union[str, Path, PathLike]) -> None:
        if isinstance(path, str):
            path = Path(path)
      
        if not path.exists() or not path.is_dir():
            raise NotADirectoryError("not a valid path for writing file")

        # Add filename to compiled filename
        path /= self.full_filename
        
        # Write bytes to specified path
        path.write_bytes(self.uu_decoded_bytes)


class UUDecodedFile(BaseUUFile):
    """
    """
    def __init__(
        self,
        file_name: str,
        permissions_mode: str,
        end_footer_included: bool,
        file_mime_type: str,
        file_extension: str
    ):
        super().__init__(
            file_name=file_name,
            permissions_mode=permissions_mode,
            file_mime_type=file_mime_type,
            file_extension=file_extension
        )

        self.end_footer_included = end_footer_included

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        class_repr = (
            f'{self.__class__.__name__}('
            f'file_name={self.file_name}, '
            f'permissions_mode={self.permissions_mode}, '
            f'file_mime_type={self.file_mime_type}, '
            f'file_extension={self.file_extension}, '
            f'end_footer_included={self.end_footer_included})'
        )
        return dedent(text=class_repr)


class UUEncodedFile(BaseUUFile):
    """
    """
    def __init__(
        self,
        file_name: str,
        permissions_mode: str,
        file_mime_type: str,
        file_extension: str
    ):
        super().__init__(
            file_name=file_name,
            permissions_mode=permissions_mode,
            file_mime_type=file_mime_type,
            file_extension=file_extension
        )

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        class_repr = (
            f'{self.__class__.__name__}('
            f'file_name={self.file_name}, '
            f'permissions_mode={self.permissions_mode}, '
            f'file_mime_type={self.file_mime_type}, '
            f'file_extension={self.file_extension})'
        )
        return dedent(text=class_repr)