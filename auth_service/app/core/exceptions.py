from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    status_code: int = 500

    def __init__(self, detail: str):
        super().__init__(status_code=self.status_code, detail=detail)


class UserAlreadyExistsError(BaseHTTPException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self):
        super().__init__("User with this email already exists")


class InvalidCredentialsError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        super().__init__("Invalid credentials")


class InvalidTokenError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        super().__init__("Invalid token")


class TokenExpiredError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        super().__init__("Token has expired")


class UserNotFoundError(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self):
        super().__init__("User not found")


class PermissionDeniedError(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self):
        super().__init__("Permission denied")
