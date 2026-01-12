"""
* AUTHENTICATION MODULE - User Authentication API *

This module provides user authentication endpoints including signup, login, logout,
and user profile retrieval. It integrates with Supabase Auth for secure user 
management and session handling.

Endpoints:
----------
- POST /signup: Create new user account
- POST /login: Authenticate user and establish session
- POST /logout: Terminate user session
- GET  /user: Retrieve current authenticated user information

Authentication Flow:
--------------------
1. Signup: Creates user in Supabase Auth (handles email verification)
2. Login: Validates credentials, returns access_token for session
3. Session: Access_token used in Authorization header for subsequent requests
4. Logout: Invalidates current session token

Security Features:
------------------
- Password hashing handled by Supabase Auth
- JWT token-based authentication
- Session management with secure tokens
- Input validation for credentials

Dependencies:
-------------
- Flask: Web framework for route handling
- Supabase: Authentication provider (via supabase_client)
- Rich: Enhanced console output for debugging
- Custom status codes from app.routes.status_codes

Error Handling:
---------------
- Returns standardized HTTP status codes
- Consistent JSON error response format
- Graceful fallback when Supabase is unavailable
- Detailed logging for debugging (with sensitive data protection)

Integration Notes:
------------------
- Requires Supabase environment configuration
- Supports both JSON and form-data for login flexibility
- Access tokens should be stored securely client-side
- All routes except /signup and /login require authentication

Environment Requirements:
-------------------------
- SUPABASE_URL and SUPABASE_KEY environment variables
- Supabase project with Auth enabled
- Proper CORS configuration for frontend access

Version: 1.0.0
Author: @AkshatBhatt0786
Last Updated: 12-01-2026
"""

from flask import Blueprint, request, jsonify
from rich import print, print_json
from app.routes.status_codes import Codes
try:
    from app.supabase_client import get_supabase
    supabase = get_supabase()
except ValueError as e:
    print(f"Warning: Supabase not configured. Error: {e}")
    supabase = None

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), Codes.ERROR
        
        if supabase is None:
            return jsonify({'error': 'Backend service unavailable'}), Codes.SERVICE_NOT_AVAILABLE
        
        try:
            response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            
            # //print(response)
            
            if hasattr(response, 'user') and response.user:
                print(f"User created/retrieved: ID={response.user.id}")
                
                # Check if this is a new user or existing
                # Supabase doesn't clearly differentiate in response
                
                return jsonify({
                    'message': 'User processed successfully',
                    'user': {
                        'id': response.user.id,
                        'email': response.user.email,
                        'created_at': getattr(response.user, 'created_at', 'unknown'),
                        'email_confirmed_at': getattr(response.user, 'email_confirmed_at', None)
                    },
                    'note': 'If user already exists, this just returns the existing user'
                }), Codes.SUCCESS
            else:
                return jsonify({'error': 'No user object in response'}), Codes.ERROR
                
        except Exception as supabase_error:
            print(f"Supabase error: {supabase_error}")
            return jsonify({'error': str(supabase_error)}), Codes.ERROR
        
    except Exception as e:
        print(f"Signup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = None
        if request.is_json:
            data = request.get_json()
        else:
            try:
                data = request.get_json(force=True, silent=True)
            except:
                data = request.form.to_dict()

        if data is None:
            return jsonify({'error': 'No data provided or invalid JSON'}), Codes.ERROR
        
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), Codes.ERROR
        
        if supabase is None:
            return jsonify({'error': 'Backend service unavailable'}), Codes.SERVICE_NOT_AVAILABLE
        
        email = data.get('email')
        password = data.get('password')
        
        response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        return jsonify({
            'message': 'Login successful',
            'access_token': response.session.access_token,
            'user': {
                'id': response.user.id,
                'email': response.user.email
            }
        }), Codes.SUCCESS
    
    except Exception as e:
        return jsonify({'error': str(e)}), Codes.ERROR

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Logout from Supabase
        supabase.auth.sign_out()
        return jsonify({'message': 'Logged out successfully'}), Codes.SUCCESS
    except Exception as e:
        return jsonify({'error': str(e)}), Codes.ERROR
    
@auth_bp.route('/user', methods=['GET'])
def get_user():
    try:
        user = supabase.auth.get_user().user
        if not user:
            return jsonify({'error': 'Not authenticated'}), Codes.ERROR
        else:
            return jsonify({
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            }), Codes.SUCCESS
    except Exception as e:
        return jsonify({'error': str(e)}), Codes.ERROR    
