from pathlib import Path
from typing import Union
from textwrap import dedent
from abc import ABC, abstractmethod

class BaseUUFile(ABC):
    """
    Abstract base class for both uudecoded and uuencoded structures.

    Args:
        filename (str): The filename of the uudecoded/uuencoded file.
        permissions_mode (str): The Unix permissions mode of the uudecoded/uuencoded file.
        file_mime_type (str): The mime type mode of the uudecoded/uuencoded file.
        file_extension (str): The file extension of the uudecoded/uuencoded file.
    """
    def __init__(
        self,
        filename: str,
        permissions_mode: str,
        file_mime_type: str,
        file_extension: str
    ):
        self.filename = filename
        self.permissions_mode = permissions_mode
        self.file_mime_type = file_mime_type
        self.file_extension = file_extension

        self.__bytearray: bytearray = bytearray()

    @property
    def full_filename(self) -> str:
        """Full filename."""
        return f'{self.filename}.{self.file_extension}'

    @property
    def uu_bytes(self) -> bytes:
        """Bytes resulting from encoding/decoding returned as a bytes object."""
        return bytes(self.__bytearray)

    @uu_bytes.setter
    def uu_bytes(self, decoded_bytes: bytearray) -> None:
        self.__bytearray = decoded_bytes

    @abstractmethod
    def write_file(self, path: Union[str, Path]) -> None:
        pass


class UUDecodedFile(BaseUUFile):
    """
    Structure for storing and manipulating a uudecoded object. Also includes a variety
    of properties and methods.
    
    Args:
        filename (str): The filename of the uudecoded file.
        permissions_mode (str): The Unix permissions mode of the uudecoded file.
        end_footer_included (bool): Boolean indicating whether there was a footer present.
        file_mime_type (str): The mime type mode of the uudecoded file.
        file_extension (str): The file extension of the uudecoded file.
    """
    def __init__(
        self,
        filename: str,
        permissions_mode: str,
        end_footer_included: bool,
        file_mime_type: str,
        file_extension: str
    ):
        super().__init__(
            filename=filename,
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
            f'filename={self.filename}, '
            f'permissions_mode={self.permissions_mode}, '
            f'file_mime_type={self.file_mime_type}, '
            f'file_extension={self.file_extension}, '
            f'end_footer_included={self.end_footer_included})'
        )
        return dedent(text=class_repr)
    
    def write_file(self, path: Union[str, Path]) -> None:
        """
        Write the decoded bytes to a specified path.

        Args:
            path (str | Path): A path to an existing directory as a string or Path object.
        """
        if isinstance(path, str):
            path = Path(path)
      
        if not path.is_dir():
            raise NotADirectoryError("not a valid path for writing file")

        # Add filename to compiled path
        path /= self.full_filename
        
        # Write bytes to specified path
        path.write_bytes(self.uu_bytes)


class UUEncodedFile(BaseUUFile):
    """
    Structure for storing and manipulating a uuencoded object. Also includes a variety
    of properties and methods.
    
    Args:
        filename (str): The filename of the uudecoded/uuencoded file.
        permissions_mode (str): The Unix permissions mode of the uudecoded/uuencoded file.
        file_mime_type (str): The mime type mode of the uudecoded/uuencoded file.
        file_extension (str): The file extension of the uudecoded/uuencoded file.
    """
    def __init__(
        self,
        filename: str,
        permissions_mode: str,
        file_mime_type: str,
        file_extension: str
    ):
        super().__init__(
            filename=filename,
            permissions_mode=permissions_mode,
            file_mime_type=file_mime_type,
            file_extension=file_extension
        )

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        class_repr = (
            f'{self.__class__.__name__}('
            f'filename={self.filename}, '
            f'permissions_mode={self.permissions_mode}, '
            f'file_mime_type={self.file_mime_type}, '
            f'file_extension={self.file_extension})'
        )
        return dedent(text=class_repr)
    
    def write_file(self, path: Union[str, Path]) -> None:
        """
        Write the uuencoded bytes to a specified path.

        Args:
            path (str | Path): A path to an existing directory as a string or Path object.
        """
        if isinstance(path, str):
            path = Path(path)
      
        if not path.is_dir():
            raise NotADirectoryError("not a valid path for writing file")

        # Add filename to compiled path
        path /= self.filename + '.txt'
        
        # Write bytes to specified path
        path.write_bytes(self.uu_bytes)