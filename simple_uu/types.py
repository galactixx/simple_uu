from dataclasses import dataclass, field

from textwrap import dedent

@dataclass
class UUDecodedFile:
    file_name: str
    permissions_mode: str
    end_footer_included: bool

    file_mime_type: str
    file_extension: str
    
    __bytearray: bytearray = field(default=bytearray)

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

    @property
    def uu_decoded_bytes(self) -> bytes:
        return bytes(self.__bytearray)
    
    def _set_uu_bytearray(self, decoded_bytes: bytes) -> None:
        self.__bytearray = decoded_bytes
        

@dataclass
class UUEncodedFile:
    pass