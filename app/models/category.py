"""
* EVENT CATEGORY MODEL *

This model provides data access layer for event category management.
Event categories define the type of event (e.g., Wedding, Birthday, Conference)
and are used to classify and organize event plans.

Purpose:
--------
- Centralize all database operations for event_categories table
- Provide type-safe data access methods
- Ensure consistent error handling and logging
- Serve as interface between business logic and database layer

Database Schema (event_categories):
-----------------------------------
table structure:
    id: Integer (Primary Key, Auto-increment)
    name: String (Category name, e.g., "Wedding", "Birthday")
    description: String (Optional description)
    icon: String (Optional icon identifier)
    created_at: Timestamp (Auto-generated)
    updated_at: Timestamp (Auto-generated)

Usage Examples:
---------------
    # Get all categories
    categories = EventCategory.get_all()
    
    # Get specific category
    category = EventCategory.get_by_id(1)

Error Handling:
---------------
- Returns empty list [] for get_all() on error
- Returns None for get_by_id() when not found or error
- Logs errors to console using rich.print for debugging
- Does not raise exceptions to calling code (graceful degradation)

Dependencies:
-------------
- datetime: For timestamp handling (if extended)
- typing: For type annotations
- rich: For enhanced console output
- app.supabase_client: Database connection

Security Notes:
---------------
- Read-only operations (no create/update/delete in current implementation)
- No user-specific data filtering (categories are global)
- No sensitive data handling

Performance Considerations:
---------------------------
- Categories are typically small datasets (<100 records)
- No pagination needed for get_all()
- Consider caching for frequently accessed categories

* Version: 1.0.0
* Author: @AkshatBhatt0786
* Last Updated: 12-01-2026
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from rich import print
from app.supabase_client import get_table

class EventCategory:
    """Event Category model"""
    
    @staticmethod
    def get_all() -> list:
        """Get all event categories"""
        try:
            response = get_table('event_categories').select('*').order('name').execute()
            return response.data
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    @staticmethod
    def get_by_id(category_id: int) -> Optional[dict]:
        """Get category by ID"""
        try:
            response = get_table('event_categories').select('*').eq('id', category_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting category: {e}")
            return None