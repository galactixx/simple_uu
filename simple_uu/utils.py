from typing import Optional, Tuple, Union
import os

def decompose_file_name(file_name_from_uu: Union[str, bytes]) -> Tuple[str, Optional[str]]:
    """
    """
    if isinstance(file_name_from_uu, bytes):
        file_name_from_uu = file_name_from_uu.decode()

    file_name, file_extension = os.path.splitext(file_name_from_uu)
    if not file_extension.startswith('.'):
        return file_name, None
    else:
        file_extension = file_extension.lstrip('.')
        return file_name, file_extension