"""
* GUEST MANAGEMENT MODELS *


This module provides comprehensive data models for guest management,
including guest information, phone numbers, and guest relationships.
It handles all database operations related to event guests and their
associated data.

Purpose:
--------
- Manage guest information for event plans
- Handle multiple phone numbers per guest
- Track guest relationships (family, friends, etc.)
- Provide RSVP tracking and invitation management
- Serve as data access layer for guest-related operations

Database Schema Overview:
------------------------
1. guests table:
    id: UUID (Primary Key)
    plan_id: UUID (Foreign Key to plans)
    name: String (Guest full name)
    email: String (Optional email address)
    phone: String (Primary phone - legacy field)
    rsvp_status: String (pending/confirmed/declined/maybe)
    is_invitation_sent: Boolean
    invitation_sent_at: Timestamp
    additional_notes: Text
    created_at/updated_at: Timestamps

2. guest_phones table:
    id: UUID (Primary Key)
    guest_id: UUID (Foreign Key to guests)
    phone_number: String
    phone_type: String (mobile/home/work)
    is_primary: Boolean
    created_at: Timestamp

3. guest_relationships table:
    id: UUID (Primary Key)
    plan_id: UUID (Foreign Key to plans)
    primary_guest_id: UUID (Foreign Key to guests)
    related_guest_id: UUID (Foreign Key to guests)
    relationship_type: String (spouse/child/parent/friend/etc.)
    notes: Text
    created_at: Timestamp

Key Features:
-------------
- Complete CRUD operations for guests
- Multiple phone numbers with type support
- Guest relationship management
- RSVP status tracking
- Invitation sent status
- Search functionality by phone number

Usage Examples:
---------------
    # Create guest with phones
    guest = Guest.create(
        plan_id='plan_uuid',
        name='John Doe',
        email='john@example.com',
        phone_numbers=[
            {'number': '+1234567890', 'type': 'mobile', 'is_primary': True},
            {'number': '+0987654321', 'type': 'home', 'is_primary': False}
        ]
    )
    
    # Update RSVP status
    Guest.update_rsvp(guest_id, 'confirmed')
    
    # Create relationship
    GuestRelationship.create_relationship(
        plan_id='plan_uuid',
        primary_guest_id='guest_1',
        related_guest_id='guest_2',
        relationship_type='spouse'
    )

* Version: 1.1.0
* Author: @AkshatBhatt0786
* Last Updated: 12-01-2026
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from rich import print
from app.supabase_client import get_table


class Guest:
    """
    Guest Data Model
    
    Handles all operations related to event guests including creation,
    updating, deletion, and querying of guest information.
    Supports multiple phone numbers per guest and RSVP tracking.
    """
    
    # Table names
    GUESTS_TABLE = 'guests'
    PHONES_TABLE = 'guest_phones'
    
    # RSVP status constants
    RSVP_PENDING = 'pending'
    RSVP_CONFIRMED = 'confirmed'
    RSVP_DECLINED = 'declined'
    RSVP_MAYBE = 'maybe'
    RSVP_OPTIONS = [RSVP_PENDING, RSVP_CONFIRMED, RSVP_DECLINED, RSVP_MAYBE]
    
    @staticmethod
    def create(plan_id: str, name: str, **kwargs) -> Optional[Dict]:
        """
        Create a new guest for an event plan
        
        Args:
            plan_id (str): UUID of the associated event plan
            name (str): Full name of the guest
            **kwargs: Additional guest properties:
                email (str, optional): Email address
                phone (str, optional): Primary phone number (legacy field)
                rsvp_status (str, optional): RSVP status (default: 'pending')
                additional_notes (str, optional): Notes about the guest
                phone_numbers (List[Dict], optional): List of phone dictionaries
        
        Returns:
            Optional[Dict]: Complete guest object with phone numbers,
                           None if creation failed
        """
        try:
            # Prepare guest data with legacy phone field support
            guest_data = {
                'plan_id': plan_id,
                'name': name,
                'email': kwargs.get('email'),
                'phone': kwargs.get('phone'),  # Legacy primary phone field
                'rsvp_status': kwargs.get('rsvp_status', Guest.RSVP_PENDING),
                'additional_notes': kwargs.get('additional_notes')
            }
            
            # Remove None values to prevent database errors
            guest_data = {k: v for k, v in guest_data.items() if v is not None}
            
            # Insert guest record
            response = get_table(Guest.GUESTS_TABLE).insert(guest_data).execute()
            guest = response.data[0] if response.data else None
            
            if not guest:
                return None
            
            # Add multiple phone numbers if provided
            phones = kwargs.get('phone_numbers', [])
            if phones:
                Guest.add_phone_numbers(guest['id'], phones)
            
            # Return complete guest information with phones
            return Guest.get_by_id(guest['id'])
            
        except Exception as e:
            print(f"Error creating guest: {e}")
            return None
    
    @staticmethod
    def add_phone_numbers(guest_id: str, phones: List[Dict]) -> List[Dict]:
        """
        Add multiple phone numbers for a guest
        
        Args:
            guest_id (str): UUID of the guest
            phones (List[Dict]): List of phone dictionaries, each containing:
                number (str): Phone number (required)
                type (str, optional): Phone type ('mobile', 'home', 'work')
                                      Default: 'mobile'
                is_primary (bool, optional): Is this the primary phone
                                             Default: False
        
        Returns:
            List[Dict]: List of created phone records, empty list on error
        """
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
            
            # Batch insert phone numbers
            response = get_table(Guest.PHONES_TABLE).insert(phone_data).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error adding phone numbers: {e}")
            return []
    
    @staticmethod
    def get_by_id(guest_id: str) -> Optional[Dict]:
        """
        Get guest by ID with all phone numbers
        
        Args:
            guest_id (str): UUID of the guest
        
        Returns:
            Optional[Dict]: Complete guest object with phone_numbers array,
                           None if guest not found
        """
        try:
            # Get guest basic information
            guest_response = get_table(Guest.GUESTS_TABLE).select('*').eq('id', guest_id).execute()
            guest = guest_response.data[0] if guest_response.data else None
            
            if not guest:
                return None
            
            # Get all associated phone numbers
            phones_response = get_table(Guest.PHONES_TABLE).select('*').eq('guest_id', guest_id).execute()
            guest['phone_numbers'] = phones_response.data if phones_response.data else []
            
            return guest
            
        except Exception as e:
            print(f"Error getting guest: {e}")
            return None
    
    @staticmethod
    def get_plan_guests(plan_id: str) -> List[Dict]:
        """
        Get all guests for a plan with their phone numbers
        
        Args:
            plan_id (str): UUID of the event plan
        
        Returns:
            List[Dict]: List of guest objects, each with phone_numbers array
        """
        try:
            # Get all guests for the plan
            guests_response = get_table(Guest.GUESTS_TABLE).select('*').eq('plan_id', plan_id).execute()
            guests = guests_response.data if guests_response.data else []
            
            # Get phone numbers for all guests in batch
            guest_ids = [guest['id'] for guest in guests]
            if guest_ids:
                phones_response = get_table(Guest.PHONES_TABLE).select('*').in_('guest_id', guest_ids).execute()
                phones = phones_response.data if phones_response.data else []
                
                # Group phones by guest_id for efficient assignment
                phones_by_guest = {}
                for phone in phones:
                    guest_id = phone['guest_id']
                    if guest_id not in phones_by_guest:
                        phones_by_guest[guest_id] = []
                    phones_by_guest[guest_id].append(phone)
                
                # Add phones to each guest
                for guest in guests:
                    guest['phone_numbers'] = phones_by_guest.get(guest['id'], [])
            
            return guests
            
        except Exception as e:
            print(f"Error getting plan guests: {e}")
            return []
    
    @staticmethod
    def update(guest_id: str, updates: Dict) -> Optional[Dict]:
        """
        Update guest information
        
        Args:
            guest_id (str): UUID of the guest to update
            updates (Dict): Dictionary of fields to update
        
        Returns:
            Optional[Dict]: Updated guest object with phone numbers,
                           None if update failed
        """
        try:
            # Perform the update
            response = get_table(Guest.GUESTS_TABLE).update(updates).eq('id', guest_id).execute()
            
            if response.data:
                # Return complete updated guest
                return Guest.get_by_id(guest_id)
            return None
            
        except Exception as e:
            print(f"Error updating guest: {e}")
            return None
    
    @staticmethod
    def update_rsvp(guest_id: str, rsvp_status: str) -> Optional[Dict]:
        """
        Update guest RSVP status
        
        Args:
            guest_id (str): UUID of the guest
            rsvp_status (str): New RSVP status
        
        Returns:
            Optional[Dict]: Updated guest object, None if update failed
        """
        return Guest.update(guest_id, {'rsvp_status': rsvp_status})
    
    @staticmethod
    def mark_invitation_sent(guest_id: str) -> Optional[Dict]:
        """
        Mark invitation as sent with current timestamp
        
        Args:
            guest_id (str): UUID of the guest
        
        Returns:
            Optional[Dict]: Updated guest object, None if update failed
        """
        updates = {
            'is_invitation_sent': True,
            'invitation_sent_at': datetime.utcnow().isoformat()
        }
        return Guest.update(guest_id, updates)
    
    @staticmethod
    def delete(guest_id: str) -> bool:
        """
        Delete a guest (cascades to phone numbers via foreign key)
        
        Args:
            guest_id (str): UUID of the guest to delete
        
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            response = get_table(Guest.GUESTS_TABLE).delete().eq('id', guest_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting guest: {e}")
            return False
    
    @staticmethod
    def search_by_phone(phone_number: str) -> List[Dict]:
        """
        Search guests by phone number
        
        Args:
            phone_number (str): Phone number to search for
        
        Returns:
            List[Dict]: List of guest objects matching the phone number,
                       each with phone_numbers array
        """
        try:
            # Search in guest_phones table
            phones_response = get_table(Guest.PHONES_TABLE).select('guest_id').eq('phone_number', phone_number).execute()
            guest_ids = [phone['guest_id'] for phone in (phones_response.data or [])]
            
            if not guest_ids:
                return []
            
            # Get guest information for found IDs
            guests_response = get_table(Guest.GUESTS_TABLE).select('*').in_('id', guest_ids).execute()
            guests = guests_response.data if guests_response.data else []
            
            # Get phone numbers for found guests
            for guest in guests:
                guest_phones = get_table(Guest.PHONES_TABLE).select('*').eq('guest_id', guest['id']).execute()
                guest['phone_numbers'] = guest_phones.data if guest_phones.data else []
            
            return guests
            
        except Exception as e:
            print(f"Error searching by phone: {e}")
            return []


class GuestRelationship:
    """
    Guest Relationship Data Model
    
    Handles relationships between guests (family connections, friendships, etc.)
    within the context of an event plan.
    """
    
    TABLE_NAME = 'guest_relationships'
    
    # Relationship type constants
    RELATIONSHIP_SPOUSE = 'spouse'
    RELATIONSHIP_CHILD = 'child'
    RELATIONSHIP_PARENT = 'parent'
    RELATIONSHIP_SIBLING = 'sibling'
    RELATIONSHIP_FRIEND = 'friend'
    RELATIONSHIP_COLLEAGUE = 'colleague'
    RELATIONSHIP_OTHER = 'other'
    RELATIONSHIP_TYPES = [
        RELATIONSHIP_SPOUSE, RELATIONSHIP_CHILD, RELATIONSHIP_PARENT,
        RELATIONSHIP_SIBLING, RELATIONSHIP_FRIEND, RELATIONSHIP_COLLEAGUE,
        RELATIONSHIP_OTHER
    ]
    
    @staticmethod
    def create_relationship(plan_id: str, primary_guest_id: str, 
                           related_guest_id: str, relationship_type: str, 
                           notes: str = None) -> Optional[Dict]:
        """
        Create a relationship between two guests
        
        Args:
            plan_id (str): UUID of the event plan
            primary_guest_id (str): UUID of the primary guest
            related_guest_id (str): UUID of the related guest
            relationship_type (str): Type of relationship
            notes (str, optional): Additional notes about the relationship
        
        Returns:
            Optional[Dict]: Created relationship object, None if creation failed
        
        Example:
            GuestRelationship.create_relationship(
                plan_id='plan_uuid',
                primary_guest_id='guest_1',
                related_guest_id='guest_2',
                relationship_type='spouse'
            )
        """
        try:
            data = {
                'plan_id': plan_id,
                'primary_guest_id': primary_guest_id,
                'related_guest_id': related_guest_id,
                'relationship_type': relationship_type,
                'notes': notes
            }
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            # Insert relationship
            response = get_table(GuestRelationship.TABLE_NAME).insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error creating relationship: {e}")
            return None
    
    @staticmethod
    def get_guest_relationships(guest_id: str) -> List[Dict]:
        """
        Get all relationships for a guest (both as primary and related)
        
        Args:
            guest_id (str): UUID of the guest
        
        Returns:
            List[Dict]: List of relationship objects with guest information
        """
        try:
            # Get relationships where guest is primary
            primary_response = get_table(GuestRelationship.TABLE_NAME) \
                .select('*, guests!guest_relationships_related_guest_id_fkey(*)') \
                .eq('primary_guest_id', guest_id).execute()
            
            # Get relationships where guest is related
            related_response = get_table(GuestRelationship.TABLE_NAME) \
                .select('*, guests!guest_relationships_primary_guest_id_fkey(*)') \
                .eq('related_guest_id', guest_id).execute()
            
            relationships = []
            if primary_response.data:
                relationships.extend(primary_response.data)
            if related_response.data:
                relationships.extend(related_response.data)
            
            return relationships
            
        except Exception as e:
            print(f"Error getting relationships: {e}")
            return []