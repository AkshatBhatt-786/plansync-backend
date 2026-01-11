from flask import Blueprint, request, jsonify
try:
    from app.supabase_client import get_supabase
    supabase = get_supabase()
except ValueError as e:
    print(f"Warning: Supabase not configured. Error: {e}")
    supabase = None

auth_bp = Blueprint('auth/accounts', __name__)

ERROR_STATUS_CODE = 400
SUCCESS_STATUS_CODE = 201

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email and not password:
            return jsonify({'error': 'Email and password is required'}), ERROR_STATUS_CODE
        else:
            response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })

            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': response.user.id,
                    'email': response.user.email
                }
            }), SUCCESS_STATUS_CODE
        
    except Exception as e:
        return jsonify({'error': str(e)}), ERROR_STATUS_CODE

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), ERROR_STATUS_CODE
        
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
        }), SUCCESS_STATUS_CODE
    
    except Exception as e:
        return jsonify({'error': str(e)}), ERROR_STATUS_CODE
    
@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Logout from Supabase
        supabase.auth.sign_out()
        return jsonify({'message': 'Logged out successfully'}), SUCCESS_STATUS_CODE
    except Exception as e:
        return jsonify({'error': str(e)}), ERROR_STATUS_CODE
    
@auth_bp.route('/user', methods=['GET'])
def get_user():
    try:
        user = supabase.auth.get_user().user
        if not user:
            return jsonify({'error': 'Not authenticated'}), ERROR_STATUS_CODE
        else:
            return jsonify({
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            }), SUCCESS_STATUS_CODE
    except Exception as e:
        return jsonify({'error': str(e)}), ERROR_STATUS_CODE    
