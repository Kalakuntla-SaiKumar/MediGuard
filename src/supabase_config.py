"""
Supabase Configuration and Database Setup
Initializes PostgreSQL connection via Supabase
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from sqlalchemy import inspect, text
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


def ensure_supabase_schema():
    """Best-effort schema sync for production Supabase deployments."""
    try:
        inspector = inspect(db.engine)
        existing = {col['name'] for col in inspector.get_columns('users')}

        required_user_columns = {
            'full_name': 'VARCHAR(120)',
            'weight': 'FLOAT',
            'blood_group': 'VARCHAR(10)',
            'phone': 'VARCHAR(20)',
            'medications': 'VARCHAR(1000)',
            'age': 'INTEGER',
            'gender': 'VARCHAR(20)',
            'pregnancy_status': 'VARCHAR(20)',
            'health_conditions': 'VARCHAR(500)',
            'allergies': 'VARCHAR(500)',
            'is_active': 'BOOLEAN DEFAULT TRUE',
            'google_id': 'VARCHAR(255)',
            'google_email': 'VARCHAR(120)',
            'auth_method': "VARCHAR(20) DEFAULT 'email'",
            'security_question_1': 'VARCHAR(255)',
            'security_answer_1': 'VARCHAR(255)',
            'security_question_2': 'VARCHAR(255)',
            'security_answer_2': 'VARCHAR(255)',
            'reset_token': 'VARCHAR(255)',
            'reset_token_expiry': 'TIMESTAMP',
            'password_reset_requested_at': 'TIMESTAMP',
        }

        with db.engine.begin() as conn:
            for col_name, col_type in required_user_columns.items():
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))

        logger.info("✓ Supabase schema sync complete")
    except Exception as e:
        # Do not block app startup if sync fails; existing schema might already be valid.
        logger.warning(f"⚠ Supabase schema sync skipped: {str(e)}")

# Import models after db is initialized
from src.supabase_models import User, AssessmentHistory

__all__ = ['db', 'supabase', 'init_supabase', 'get_db_uri', 'init_db', 'ensure_supabase_schema', 'User', 'AssessmentHistory']
