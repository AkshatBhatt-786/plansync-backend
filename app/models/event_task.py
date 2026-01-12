"""
* EVENT TASK MODEL *

This model provides data access layer for event task management.
Tasks are individual action items associated with specific event plans,
helping users organize and track event preparation activities.

Purpose:
--------
- Centralize database operations for event_tasks table
- Provide business logic for task creation and management
- Ensure data integrity with validation and error handling
- Serve as interface between controllers and database

Database Schema (event_tasks):
------------------------------
table structure:
    id: UUID (Primary Key, Auto-generated)
    plan_id: UUID (Foreign Key to plans table)
    title: String (Task title/name)
    description: Text (Optional detailed description)
    due_date: Timestamp (Optional completion deadline)
    priority: String (Task priority: 'low', 'medium', 'high')
    status: String (Task status: 'pending', 'in_progress', 'completed', 'cancelled')
    assigned_to: UUID (Optional Foreign Key to users table)
    completed_at: Timestamp (Optional completion timestamp)
    created_at: Timestamp (Auto-generated)
    updated_at: Timestamp (Auto-generated)

* Version: 1.0.0
* Author: @AkshatBhatt0786
* Last Updated: 12-01-2026
"""

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