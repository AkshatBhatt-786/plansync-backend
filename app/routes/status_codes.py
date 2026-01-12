"""
* HTTP Status Code Definitions *

This module defines standardized HTTP status codes used throughout the application
for consistent API responses. Using an Enum ensures type safety and prevents
magic numbers in the codebase.

Purpose:
--------
- Centralize all HTTP status code definitions
- Improve code readability and maintainability
- Ensure consistent response patterns across all API endpoints
- Facilitate easier debugging and error handling

Usage:
------
from app.routes.status_codes import Codes

# Return successful response
return jsonify(data), Codes.SUCCESS.value

# Return error response
return jsonify({'error': message}), Codes.ERROR.value

Note: Use .value attribute when returning from Flask routes since Flask expects
integer status codes. The Enum provides better IDE support and prevents typos.

Code Standards:
---------------
- 2xx: Success codes
- 4xx: Client error codes
- 5xx: Server error codes

Future Considerations:
----------------------
- Add more specific codes as needed (e.g., FORBIDDEN, CONFLICT, UNPROCESSABLE_ENTITY)
- Consider adding descriptive messages alongside codes
- Potentially extend to include custom application-specific codes

Maintainer: API Development Team
Version: 1.0.0
"""

from enum import Enum

class Codes(Enum):
    """Standard HTTP status codes for API responses"""
    
    # 2xx SUCCESS CODES
    SUCCESS: int = 201
    """201 Created - Request succeeded and resource was created"""
    
    # 4xx CLIENT ERROR CODES
    ERROR: int = 400
    """400 Bad Request - Client sent invalid data or malformed request"""
    
    NOT_FOUND: int = 404
    """404 Not Found - Requested resource does not exist"""
    
    UNAUTHORISED_ACCESS: int = 401
    """401 Unauthorized - Authentication required or invalid credentials"""
    
    # 5xx SERVER ERROR CODES
    SERVICE_NOT_AVAILABLE: int = 500
    """500 Internal Server Error - Unexpected server condition"""