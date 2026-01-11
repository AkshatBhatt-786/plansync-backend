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
