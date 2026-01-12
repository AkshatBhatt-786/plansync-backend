from flask import Blueprint, request, jsonify, g
from app.routes.status_codes import Codes
from app.supabase_client import get_auth
from app.models.plan import Plan
from app.models.event_task import EventTask
from app.models.guest import Guest, GuestRelationship
from app.models.category import EventCategory
from datetime import datetime
import uuid

plans_bp = Blueprint('plans', __name__)

# ==================== HELPER FUNCTIONS ====================

def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        user = get_auth().get_user(token)
        return user.user if user else None
    except:
        return None

# ==================== EVENT CATEGORIES ====================

@plans_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all event categories"""
    categories = EventCategory.get_all()
    return jsonify({'categories': categories}), Codes.SUCCESS

# ==================== PLANS/EVENTS ====================

@plans_bp.route('/', methods=['POST'])
def create_plan():
    """Create a new event plan"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), Codes.ERROR
    
    # Required fields
    title = data.get('title')
    event_date_str = data.get('event_date')
    
    if not title or not event_date_str:
        return jsonify({'error': 'Title and event_date are required'}), Codes.ERROR
    
    # Parse date
    try:
        event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
    except:
        return jsonify({'error': 'Invalid date format. Use ISO format'}), Codes.ERROR
    
    # Create a plan
    plan = Plan.create(
        user_id=user.id,
        title=title,
        event_date=event_date,
        description=data.get('description'),
        location=data.get('location'),
        category_id=data.get('category_id'),
        budget=data.get('budget'),
        guest_count=data.get('guest_count', 0),
        status=data.get('status', 'planned'),
        is_public=data.get('is_public', False)
    )
    
    if not plan:
        return jsonify({'error': 'Failed to create plan'}), 500
    
    return jsonify({
        'message': 'Plan created successfully',
        'plan': plan
    }), 201

@plans_bp.route('/', methods=['GET'])
def get_plans():
    """Get all plans for current user"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Pagination
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    plans = Plan.get_user_plans(user.id, limit=limit, offset=offset)
    
    return jsonify({
        'plans': plans,
        'count': len(plans),
        'limit': limit,
        'offset': offset
    }), Codes.SUCCESS

@plans_bp.route('/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get specific plan by ID"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    plan = Plan.get_by_id(plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), Codes.NOT_FOUND
    
    # Check ownership
    if plan['user_id'] != user.id:
        return jsonify({'error': 'Unauthorized to view this plan'}), 403
    
    # Get guests and tasks
    guests = Guest.get_plan_guests(plan_id)
    
    return jsonify({
        'plan': plan,
        'guests': guests,
        'guests_count': len(guests)
    }), Codes.SUCCESS

@plans_bp.route('/<plan_id>', methods=['PUT'])
def update_plan(plan_id):
    """Update a plan"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    data = request.json
    if not data:
        return jsonify({'error': 'No update data provided'}), Codes.ERROR
    
    # Update plan
    updated = Plan.update(plan_id, data)
    if not updated:
        return jsonify({'error': 'Failed to update plan'}), 500
    
    return jsonify({
        'message': 'Plan updated successfully',
        'plan': updated
    }), Codes.SUCCESS

@plans_bp.route('/<plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """Delete a plan"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    # Delete plan
    success = Plan.delete(plan_id)
    if not success:
        return jsonify({'error': 'Failed to delete plan'}), 500
    
    return jsonify({'message': 'Plan deleted successfully'}), Codes.SUCCESS

# ==================== GUESTS ====================
# ==================== GUESTS (Enhanced) ====================

@plans_bp.route('/<plan_id>/guests', methods=['POST'])
def add_guest(plan_id):
    """Add guest to a plan with multiple phone numbers"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    data = request.json
    if not data:
        return jsonify({'error': 'No guest data provided'}), Codes.ERROR
    
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Guest name is required'}), Codes.ERROR
    
    # Process phone numbers
    phone_numbers = data.get('phone_numbers', [])
    
    # If single phone provided (backward compatibility)
    if data.get('phone') and not phone_numbers:
        phone_numbers = [{
            'number': data.get('phone'),
            'type': 'mobile',
            'is_primary': True
        }]
    
    # Validate phone numbers
    for phone in phone_numbers:
        if not phone.get('number'):
            return jsonify({'error': 'Phone number is required in phone_numbers'}), Codes.ERROR
    
    # Add guest
    guest = Guest.create(
        plan_id=plan_id,
        name=name,
        email=data.get('email'),
        phone=data.get('phone'),  # Primary phone (backward compatibility)
        rsvp_status=data.get('rsvp_status', 'pending'),
        additional_notes=data.get('additional_notes'),
        phone_numbers=phone_numbers
    )
    
    if not guest:
        return jsonify({'error': 'Failed to add guest'}), 500
    
    # Update guest count
    Plan.update(plan_id, {'guest_count': plan['guest_count'] + 1})
    
    return jsonify({
        'message': 'Guest added successfully',
        'guest': guest
    }), 201

@plans_bp.route('/<plan_id>/guests', methods=['GET'])
def get_guests(plan_id):
    """Get all guests for a plan with phone numbers"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    guests = Guest.get_plan_guests(plan_id)
    
    # RSVP statistics
    rsvp_stats = {
        'pending': 0,
        'confirmed': 0,
        'declined': 0,
        'maybe': 0
    }
    
    for guest in guests:
        status = guest.get('rsvp_status', 'pending')
        if status in rsvp_stats:
            rsvp_stats[status] += 1
    
    return jsonify({
        'guests': guests,
        'count': len(guests),
        'rsvp_stats': rsvp_stats
    }), Codes.SUCCESS

@plans_bp.route('/<plan_id>/guests/<guest_id>', methods=['GET'])
def get_guest(plan_id, guest_id):
    """Get specific guest details"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    guest = Guest.get_by_id(guest_id)
    if not guest:
        return jsonify({'error': 'Guest not found'}), Codes.NOT_FOUND
    
    # Check if guest belongs to this plan
    if guest['plan_id'] != plan_id:
        return jsonify({'error': 'Guest does not belong to this plan'}), Codes.ERROR
    
    return jsonify({'guest': guest}), Codes.SUCCESS

@plans_bp.route('/<plan_id>/guests/<guest_id>', methods=['PUT'])
def update_guest(plan_id, guest_id):
    """Update guest information"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    data = request.json
    if not data:
        return jsonify({'error': 'No update data provided'}), Codes.ERROR
    
    # Update guest
    guest = Guest.update(guest_id, data)
    if not guest:
        return jsonify({'error': 'Failed to update guest'}), 500
    
    return jsonify({
        'message': 'Guest updated successfully',
        'guest': guest
    }), Codes.SUCCESS

@plans_bp.route('/<plan_id>/guests/<guest_id>', methods=['DELETE'])
def delete_guest(plan_id, guest_id):
    """Delete a guest"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    # Delete guest
    success = Guest.delete(guest_id)
    if not success:
        return jsonify({'error': 'Failed to delete guest'}), 500
    
    # Update guest count
    Plan.update(plan_id, {'guest_count': max(0, plan['guest_count'] - 1)})
    
    return jsonify({'message': 'Guest deleted successfully'}), Codes.SUCCESS

@plans_bp.route('/<plan_id>/guests/<guest_id>/rsvp', methods=['PUT'])
def update_guest_rsvp(plan_id, guest_id):
    """Update guest RSVP status"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    data = request.json
    rsvp_status = data.get('rsvp_status')
    
    if not rsvp_status or rsvp_status not in ['pending', 'confirmed', 'declined', 'maybe']:
        return jsonify({'error': 'Valid RSVP status required'}), Codes.ERROR
    
    # Update RSVP
    guest = Guest.update_rsvp(guest_id, rsvp_status)
    if not guest:
        return jsonify({'error': 'Failed to update RSVP'}), 500
    
    return jsonify({
        'message': f'RSVP updated to {rsvp_status}',
        'guest': guest
    }), Codes.SUCCESS

@plans_bp.route('/<plan_id>/guests/<guest_id>/invite', methods=['POST'])
def send_invitation(plan_id, guest_id):
    """Mark invitation as sent (or trigger sending)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    # Mark invitation as sent
    guest = Guest.mark_invitation_sent(guest_id)
    if not guest:
        return jsonify({'error': 'Failed to mark invitation'}), 500
    
    return jsonify({
        'message': 'Invitation marked as sent',
        'guest': guest
    }), Codes.SUCCESS

# ==================== GUEST PHONES ====================

@plans_bp.route('/<plan_id>/guests/<guest_id>/phones', methods=['POST'])
def add_guest_phone(plan_id, guest_id):
    """Add phone number to guest"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check authorization
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    data = request.json
    if not data or not data.get('phone_number'):
        return jsonify({'error': 'Phone number is required'}), Codes.ERROR
    
    # Add phone
    phone_data = [{
        'number': data['phone_number'],
        'type': data.get('phone_type', 'mobile'),
        'is_primary': data.get('is_primary', False)
    }]
    
    phones = Guest.add_phone_numbers(guest_id, phone_data)
    if not phones:
        return jsonify({'error': 'Failed to add phone number'}), 500
    
    return jsonify({
        'message': 'Phone number added successfully',
        'phone': phones[0] if phones else None
    }), 201

# ==================== TASKS ====================

@plans_bp.route('/<plan_id>/tasks', methods=['POST'])
def create_task(plan_id):
    """Create a task for a plan"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    # Check if plan exists and belongs to user
    plan = Plan.get_by_id(plan_id)
    if not plan or plan['user_id'] != user.id:
        return jsonify({'error': 'Plan not found or unauthorized'}), Codes.NOT_FOUND
    
    data = request.json
    if not data:
        return jsonify({'error': 'No task data provided'}), Codes.ERROR
    
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Task title is required'}), Codes.ERROR
    
    # Parse due date if provided
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid due_date format'}), Codes.ERROR
    
    # Create task
    task = EventTask.create_task(
        plan_id=plan_id,
        title=title,
        description=data.get('description'),
        due_date=due_date.isoformat() if due_date else None,
        priority=data.get('priority', 'medium'),
        assigned_to=data.get('assigned_to')
    )
    
    if not task:
        return jsonify({'error': 'Failed to create task'}), 500
    
    return jsonify({
        'message': 'Task created successfully',
        'task': task
    }), 201

# ==================== STATISTICS ====================

@plans_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get user's event statistics"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), Codes.UNAUTHORISED_ACCESS
    
    plans = Plan.get_user_plans(user.id, limit=1000)
    
    stats = {
        'total_plans': len(plans),
        'upcoming_plans': len([p for p in plans if p['status'] == 'planned']),
        'completed_plans': len([p for p in plans if p['status'] == 'completed']),
        'total_guests': sum(p.get('guest_count', 0) for p in plans),
        'by_category': {}
    }
    
    # Count by category
    for plan in plans:
        category = plan.get('category_id')
        if category:
            stats['by_category'][str(category)] = stats['by_category'].get(str(category), 0) + 1
    
    return jsonify({'stats': stats}), Codes.SUCCESS