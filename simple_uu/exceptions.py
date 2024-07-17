class BaseError(Exception):
    """Base error class."""
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message


class InvalidUUDecodingError(BaseError):
    """Error with decoding uuencoded data."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidUUEncodingError(BaseError):
    """Error with encoding data to a uuencoded format."""
    def __init__(self, message: str):
        super().__init__(message=message)


class InvalidPermissionsMode(BaseError):
    """Error with the the permissions mode."""
    def __init__(self, message: str):
        super().__init__(message=message)


class FileExtensionNotFoundError(BaseError):
    """
    Error that occurs when decoding uuencoded data, where the file type
    could not be detected from signature and no file extension was found in header.
    """
    def __init__(self, message: str):
        super().__init__(message=message)


class FileExtensionNotDetected(BaseError):
    """
    Error that occurs when encoding data in a uuencoded format, where the
    file type could not be detected from signature and no file extension was provided.
    """
    def __init__(self, message: str):
        super().__init__(message=message)
