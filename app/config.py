import os

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