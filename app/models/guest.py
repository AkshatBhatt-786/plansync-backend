from datetime import datetime
from typing import Optional, Dict, List, Any
from rich import print
from app.supabase_client import get_table

class Guest:
    
    @staticmethod
    def create(plan_id: str, name: str, **kwargs) -> Optional[Dict]:
        try:
            guest_data = {
                'plan_id': plan_id,
                'name': name,
                'email': kwargs.get('email'),
                'phone': kwargs.get('phone'),  # Primary phone
                'rsvp_status': kwargs.get('rsvp_status', 'pending'),
                'additional_notes': kwargs.get('additional_notes')
            }
            
            # Remove None values
            guest_data = {k: v for k, v in guest_data.items() if v is not None}
            
            response = get_table('guests').insert(guest_data).execute()
            guest = response.data[0] if response.data else None
            
            if not guest:
                return None
            
            # adding phone numbers if provided
            phones = kwargs.get('phone_numbers', [])
            if phones:
                Guest.add_phone_numbers(guest['id'], phones)
            
            # Get complete guest with phones
            return Guest.get_by_id(guest['id'])
            
        except Exception as e:
            print(f"Error creating guest: {e}")
            return None
    
    @staticmethod
    def add_phone_numbers(guest_id: str, phones: List[Dict]) -> List[Dict]:
        """Add multiple phone numbers for a guest"""
        try:
            phone_data = []
            for phone in phones:
                phone_entry = {
                    'guest_id': guest_id,
                    'phone_number': phone.get('number'),
                    'phone_type': phone.get('type', 'mobile'),
                    'is_primary': phone.get('is_primary', False)
                }
                phone_data.append(phone_entry)
            
            response = get_table('guest_phones').insert(phone_data).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error adding phone numbers: {e}")
            return []
    
    @staticmethod
    def get_by_id(guest_id: str) -> Optional[Dict]:
        """Get guest by ID with all phone numbers"""
        try:
            # Get guest
            guest_response = get_table('guests').select('*').eq('id', guest_id).execute()
            guest = guest_response.data[0] if guest_response.data else None
            
            if not guest:
                return None
            
            # Get phone numbers
            phones_response = get_table('guest_phones').select('*').eq('guest_id', guest_id).execute()
            guest['phone_numbers'] = phones_response.data if phones_response.data else []
            
            return guest
            
        except Exception as e:
            print(f"Error getting guest: {e}")
            return None
    
    @staticmethod
    def get_plan_guests(plan_id: str) -> List[Dict]:
        """Get all guests for a plan with their phone numbers"""
        try:
            # Get guests
            guests_response = get_table('guests').select('*').eq('plan_id', plan_id).execute()
            guests = guests_response.data if guests_response.data else []
            
            # Get phone numbers for all guests
            guest_ids = [guest['id'] for guest in guests]
            if guest_ids:
                phones_response = get_table('guest_phones').select('*').in_('guest_id', guest_ids).execute()
                phones = phones_response.data if phones_response.data else []
                
                # Group phones by guest_id
                phones_by_guest = {}
                for phone in phones:
                    guest_id = phone['guest_id']
                    if guest_id not in phones_by_guest:
                        phones_by_guest[guest_id] = []
                    phones_by_guest[guest_id].append(phone)
                
                # Add phones to guests
                for guest in guests:
                    guest['phone_numbers'] = phones_by_guest.get(guest['id'], [])
            
            return guests
            
        except Exception as e:
            print(f"Error getting plan guests: {e}")
            return []
    
    @staticmethod
    def update(guest_id: str, updates: Dict) -> Optional[Dict]:
        """Update guest information"""
        try:
            # Update guest
            response = get_table('guests').update(updates).eq('id', guest_id).execute()
            
            if response.data:
                # Return updated guest with phones
                return Guest.get_by_id(guest_id)
            return None
            
        except Exception as e:
            print(f"Error updating guest: {e}")
            return None
    
    @staticmethod
    def update_rsvp(guest_id: str, rsvp_status: str) -> Optional[Dict]:
        """Update guest RSVP status"""
        return Guest.update(guest_id, {'rsvp_status': rsvp_status})
    
    @staticmethod
    def mark_invitation_sent(guest_id: str) -> Optional[Dict]:
        """Mark invitation as sent"""
        from datetime import datetime
        
        updates = {
            'is_invitation_sent': True,
            'invitation_sent_at': datetime.utcnow().isoformat()
        }
        return Guest.update(guest_id, updates)
    
    @staticmethod
    def delete(guest_id: str) -> bool:
        """Delete a guest (cascade will delete phones)"""
        try:
            response = get_table('guests').delete().eq('id', guest_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting guest: {e}")
            return False
    
    @staticmethod
    def search_by_phone(phone_number: str) -> List[Dict]:
        """Search guests by phone number"""
        try:
            # Search in guest_phones
            phones_response = get_table('guest_phones').select('guest_id').eq('phone_number', phone_number).execute()
            guest_ids = [phone['guest_id'] for phone in (phones_response.data or [])]
            
            if not guest_ids:
                return []
            
            # Get guests
            guests_response = get_table('guests').select('*').in_('id', guest_ids).execute()
            guests = guests_response.data if guests_response.data else []
            
            # Get phone numbers for found guests
            for guest in guests:
                guest_phones = get_table('guest_phones').select('*').eq('guest_id', guest['id']).execute()
                guest['phone_numbers'] = guest_phones.data if guest_phones.data else []
            
            return guests
            
        except Exception as e:
            print(f"Error searching by phone: {e}")
            return []

class GuestRelationship:
    """Manage relationships between guests"""
    
    @staticmethod
    def create_relationship(plan_id: str, primary_guest_id: str, related_guest_id: str, 
                           relationship_type: str, notes: str = None) -> Optional[Dict]:
        """Create relationship between two guests"""
        try:
            data = {
                'plan_id': plan_id,
                'primary_guest_id': primary_guest_id,
                'related_guest_id': related_guest_id,
                'relationship_type': relationship_type,
                'notes': notes
            }
            
            data = {k: v for k, v in data.items() if v is not None}
            
            response = get_table('guest_relationships').insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error creating relationship: {e}")
            return None
    
    @staticmethod
    def get_guest_relationships(guest_id: str) -> List[Dict]:
        """Get all relationships for a guest"""
        try:
            # As primary guest
            primary_response = get_table('guest_relationships').select('*, guests!guest_relationships_related_guest_id_fkey(*)').eq('primary_guest_id', guest_id).execute()
            
            # As related guest
            related_response = get_table('guest_relationships').select('*, guests!guest_relationships_primary_guest_id_fkey(*)').eq('related_guest_id', guest_id).execute()
            
            relationships = []
            if primary_response.data:
                relationships.extend(primary_response.data)
            if related_response.data:
                relationships.extend(related_response.data)
            
            return relationships
            
        except Exception as e:
            print(f"Error getting relationships: {e}")
            return []