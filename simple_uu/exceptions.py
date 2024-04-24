class BaseError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class InvalidUUEncodedFileError(BaseError):
    def __init__(self, message: str):
        super().__init__(message)


class FileExtensionNotFoundError(BaseError):
    def __init__(self):
        super().__init__(
            message='the file extension was not found in header, and could not be detected from the signature'
        )