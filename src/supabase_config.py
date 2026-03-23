"""
Supabase Configuration and Database Setup
Initializes PostgreSQL connection via Supabase
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy for PostgreSQL (via Supabase)
db = SQLAlchemy()

# Supabase client (for auth operations)
supabase: Client = None

def init_supabase():
    """Initialize Supabase client with credentials from environment"""
    global supabase
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    
    supabase = create_client(supabase_url, supabase_key)
    logger.info("✓ Supabase client initialized")
    return supabase

def get_db_uri():
    """Get PostgreSQL connection string from environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("Missing DATABASE_URL environment variable")
    
    # SQLAlchemy requires postgresql+psycopg2 instead of postgresql
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    return database_url

def init_db(app):
    """Initialize database with Flask app"""
    with app.app_context():
        db.create_all()
        logger.info("✓ Database initialized (PostgreSQL via Supabase)")

# Import models after db is initialized
from src.supabase_models import User, AssessmentHistory

__all__ = ['db', 'supabase', 'init_supabase', 'get_db_uri', 'init_db', 'User', 'AssessmentHistory']
