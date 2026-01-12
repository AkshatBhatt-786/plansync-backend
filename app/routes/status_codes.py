from enum import Enum

class Codes(Enum):
    SUCCESS: int = 201
    ERROR: int = 400
    NOT_FOUND: int = 404
    SERVICE_NOT_AVAILABLE: int = 500
    UNAUTHORISED_ACCESS: int = 401
    