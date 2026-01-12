"""
* PLAN DATA MODEL *

This model provides the data access layer for event plan management.
Plans represent the core entities in the application, containing all
information about events being organized by users.

Purpose:
--------
- Centralize all database operations for plans table
- Handle plan creation, retrieval, updating, and deletion
- Provide user-specific plan querying with pagination
- Manage plan status and metadata
- Serve as interface between controllers and database

Database Schema (plans):
------------------------
table structure:
    id: UUID (Primary Key, Auto-generated)
    user_id: UUID (Foreign Key to auth.users)
    title: String (Event title/name)
    event_date: Timestamp (Date and time of event)
    description: Text (Optional detailed description)
    location: String (Optional event location)
    category_id: Integer (Foreign Key to event_categories)
    budget: Decimal (Optional budget amount)
    guest_count: Integer (Count of invited guests)
    status: String (Event status: 'planned', 'in_progress', 'completed', 'cancelled')
    is_public: Boolean (Whether plan is publicly visible)
    created_at: Timestamp (Auto-generated)
    updated_at: Timestamp (Auto-updated on modification)

Relationships:
--------------
- One-to-many: User -> Plans
- One-to-many: EventCategory -> Plans
- One-to-many: Plan -> Guests
- One-to-many: Plan -> EventTasks

Key Features:
-------------
- Complete CRUD operations for plans
- User-specific plan retrieval with pagination
- Automatic timestamp management
- Category information joins for enriched data
- Comprehensive error handling

Usage Examples:
---------------
    
    # Get user's plans with pagination
    plans = Plan.get_user_plans(user_id='user_uuid', limit=20, offset=0)
    
    # Update plan status
    Plan.update(plan_id='plan_uuid', updates={'status': 'completed'})
    
    # Delete a plan
    Plan.delete(plan_id='plan_uuid')

Error Handling:
---------------
- Returns None for single-object operations on error
- Returns empty list [] for collection operations on error
- Logs detailed error information for debugging
- Graceful degradation to prevent application crashes
- Input validation responsibility of calling code

Dependencies:
-------------
- datetime: For timestamp handling and date operations
- typing: For type annotations
- rich: For enhanced console logging
- app.supabase_client: Database connection

Security Notes:
---------------
- User ownership validation required in controller layer
- Private plans only accessible to owner
- Budget and guest count should be validated for reasonable values
- SQL injection prevention via parameterized queries

Performance Considerations:
---------------------------
- Indexes needed on: user_id, event_date, status, category_id
- Pagination support for users with many plans
- Category joins are efficient due to small category table
- Consider materialized views for complex plan statistics

Future Enhancements:
--------------------
- Plan sharing and collaboration features
- Plan templates and duplication
- Advanced filtering and search
- Plan versioning/history
- Export functionality (PDF, CSV)
- Plan analytics and insights

* Version: 1.0.0
* Author: @AkshatBhatt0786
* Last Updated: 12-01-2026
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from rich import print
from app.supabase_client import get_table

class Plan:

    @staticmethod
    def create(user_id: str, title: str, event_date: datetime, **kwargs) -> Optional[Dict]:
        try:
            data = {
                'user_id': user_id,
                'title': title,
                'event_date': event_date.isoformat(),
                'description': kwargs.get('description'),
                'location': kwargs.get('location'),
                'category_id': kwargs.get('category_id'),
                'budget': kwargs.get('budget'),
                'guest_count': kwargs.get('guest_count', 0),
                'status': kwargs.get('status', 'planned'),
                'is_public': kwargs.get('is_public', False)
            }

            # removing none values
            data = {k: v for k, v in data.items() if v is not None}

            response = get_table('plans').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating a plan: {e}")
    
    @staticmethod
    def get_by_id(plan_id: str) -> Optional[Dict]:
        try:
            response = get_table('plans').select('*').eq('id', plan_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting plan: {e}")
            return None
    
    @staticmethod
    def get_user_plans(user_id: str, limit: int = 50, offset: int = 0) -> list:
        try:
            response = (
                get_table('plans')
                .select('*, event_categories(name, icon)')
                .eq('user_id', user_id)
                .order('event_date', desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error getting user plans: {e}")
            return []
    
    @staticmethod
    def update(plan_id: str, updates: Dict) -> Optional[Dict]:
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            response = get_table('plans').update(updates).eq('id', plan_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating plan: {e}")
            return None
    
    @staticmethod
    def delete(plan_id: str) -> bool:
        try:
            response = get_table('plans').delete().eq('id', plan_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting plan: {e}")
            return False
