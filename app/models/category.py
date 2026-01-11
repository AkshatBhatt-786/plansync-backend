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