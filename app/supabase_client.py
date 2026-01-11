import os
from config import config
from flask import current_app
from supabase import create_client, Client

class SupabaseClient:
    _instance: Client = None

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            supabase_url = config.get('development').SUPABASE_URL
            supabase_key = config.get('developement').SUPABASE_KEY

            if not supabase_url or not supabase_key:
                raise ValueError("Supabase URL and Key must be set in environment variables")
            else:
                cls._instance = create_client(supabase_url, supabase_key)
        return cls._instance

    @classmethod
    def auth(cls):
        return cls.get_client().auth
    
    @classmethod
    def table(cls, table_name):
        return cls.get_client().table(table_name)
    
def get_supabase():
    return SupabaseClient.get_client()

def get_auth():
    return SupabaseClient.auth()

def get_table(table_name: str):
    return SupabaseClient.table(table_name)