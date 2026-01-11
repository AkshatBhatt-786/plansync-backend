import os
from pathlib import Path
from dotenv import load_dotenv
from rich import print


env_path = Path('.') / '.env.example'
print(f"Loading [bold red].env[/] from: [blue u]{env_path.absolute()}[/]")
print(f".env exists: [bold green]{'201' if env_path.exists() else '400'}[/]")  
load_dotenv(env_path)

# Author: @AkshatBhatt-786
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dragon@ocean786')

    # SUPABASE-CONFIGURATIONS
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

class DevConfig(Config):
    DEBUG = True

config = {
    'development': DevConfig,
    'default': DevConfig
}