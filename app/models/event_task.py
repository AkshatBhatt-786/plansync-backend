from datetime import datetime
from typing import Optional, Dict, List, Any
from rich import print
from app.supabase_client import get_table

class EventTask:
    """Event Task Model"""
    
    @staticmethod
    def create_task(plan_id: str, title: str, **kwargs) -> Optional[Dict]:
        """Create a new task for a plan"""
        try:
            data = {
                'plan_id': plan_id,
                'title': title,
                'description': kwargs.get('description'),
                'due_date': kwargs.get('due_date'),
                'priority': kwargs.get('priority', 'medium'),
                'assigned_to': kwargs.get('assigned_to')
            }
            
            data = {k: v for k, v in data.items() if v is not None}
            
            response = get_table('event_tasks').insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error creating task: {e}")
            return None