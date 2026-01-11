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
