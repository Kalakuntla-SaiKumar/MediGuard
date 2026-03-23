"""
Migration Script: SQLite to Supabase (PostgreSQL)
Migrates existing user data and assessments to Supabase

Usage:
    python migrate_to_supabase.py
"""

import os
import sys
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def migrate():
    """Migrate data from SQLite to Supabase"""
    
    print("\n" + "="*60)
    print("  MediGuard: SQLite → Supabase Migration")
    print("="*60)
    
    # Step 1: Setup Supabase connection
    print("\n[1/4] Initializing Supabase connection...")
    try:
        from src.supabase_config import db, init_supabase, get_db_uri
        from src.supabase_models import User, AssessmentHistory
        from flask import Flask
        
        # Create Flask app
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Create tables
            print("   Creating tables in Supabase...")
            db.create_all()
            print("   ✓ Tables created")
        
        init_supabase()
        print("   ✓ Supabase initialized")
    except Exception as e:
        print(f"   ✗ Error initializing Supabase: {e}")
        print("\n   Make sure you have:")
        print("   - Installed: pip install -r requirements-supabase.txt")
        print("   - Set env vars: SUPABASE_URL, SUPABASE_KEY, DATABASE_URL")
        return False
    
    # Step 2: Read from SQLite
    print("\n[2/4] Reading data from SQLite...")
    sqlite_db = os.path.join(PROJECT_ROOT, "mediguard.db")
    
    if not os.path.exists(sqlite_db):
        print(f"   ℹ No SQLite database found at {sqlite_db}")
        print("   Creating empty Supabase tables only...")
        print("   ✓ Ready for new users")
        return True
    
    try:
        conn = sqlite3.connect(sqlite_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Read users
        cursor.execute("SELECT * FROM users")
        users_data = [dict(row) for row in cursor.fetchall()]
        print(f"   Found {len(users_data)} users")
        
        # Read assessments
        cursor.execute("SELECT * FROM assessment_history")
        assessments_data = [dict(row) for row in cursor.fetchall()]
        print(f"   Found {len(assessments_data)} assessments")
        
        conn.close()
    except Exception as e:
        print(f"   ✗ Error reading SQLite: {e}")
        return False
    
    # Step 3: Migrate to Supabase
    print("\n[3/4] Migrating data to Supabase...")
    
    try:
        with app.app_context():
            # Migrate users
            user_mapping = {}  # Map old SQLite IDs to new UUIDs
            
            for user_data in users_data:
                try:
                    old_id = user_data.get('id')
                    
                    # Create new user with UUID
                    user = User(
                        email=user_data.get('email'),
                        username=user_data.get('username'),
                        password_hash=user_data.get('password_hash'),
                        full_name=user_data.get('full_name'),
                        weight=user_data.get('weight'),
                        blood_group=user_data.get('blood_group'),
                        phone=user_data.get('phone'),
                        medications=user_data.get('medications'),
                        age=user_data.get('age'),
                        gender=user_data.get('gender'),
                        pregnancy_status=user_data.get('pregnancy_status'),
                        health_conditions=user_data.get('health_conditions'),
                        allergies=user_data.get('allergies'),
                        is_active=user_data.get('is_active', True),
                        google_id=user_data.get('google_id'),
                        google_email=user_data.get('google_email'),
                        auth_method=user_data.get('auth_method', 'email'),
                        security_question_1=user_data.get('security_question_1'),
                        security_answer_1=user_data.get('security_answer_1'),
                        security_question_2=user_data.get('security_question_2'),
                        security_answer_2=user_data.get('security_answer_2'),
                        reset_token=user_data.get('reset_token'),
                        created_at=datetime.fromisoformat(user_data.get('created_at')) if user_data.get('created_at') else datetime.utcnow(),
                        updated_at=datetime.fromisoformat(user_data.get('updated_at')) if user_data.get('updated_at') else datetime.utcnow(),
                    )
                    
                    db.session.add(user)
                    db.session.flush()  # Get the new UUID
                    user_mapping[old_id] = user.id
                    
                except Exception as e:
                    print(f"   ⚠ Error migrating user {user_data.get('username')}: {e}")
                    db.session.rollback()
                    continue
            
            print(f"   ✓ Migrated {len(user_mapping)} users")
            
            # Migrate assessments
            migrated_assessments = 0
            for assessment_data in assessments_data:
                try:
                    old_user_id = assessment_data.get('user_id')
                    new_user_id = user_mapping.get(old_user_id)
                    
                    if not new_user_id:
                        continue  # Skip if user not migrated
                    
                    assessment = AssessmentHistory(
                        user_id=new_user_id,
                        drug1=assessment_data.get('drug1'),
                        drug2=assessment_data.get('drug2'),
                        condition=assessment_data.get('condition'),
                        ddi_risk=assessment_data.get('ddi_risk'),
                        dfi_risk_drug1=assessment_data.get('dfi_risk_drug1'),
                        dfi_risk_drug2=assessment_data.get('dfi_risk_drug2'),
                        dci_risk_drug1=assessment_data.get('dci_risk_drug1'),
                        dci_risk_drug2=assessment_data.get('dci_risk_drug2'),
                        overall_risk=assessment_data.get('overall_risk'),
                        created_at=datetime.fromisoformat(assessment_data.get('created_at')) if assessment_data.get('created_at') else datetime.utcnow(),
                    )
                    
                    db.session.add(assessment)
                    migrated_assessments += 1
                    
                except Exception as e:
                    print(f"   ⚠ Error migrating assessment: {e}")
                    db.session.rollback()
                    continue
            
            # Commit all changes
            db.session.commit()
            print(f"   ✓ Migrated {migrated_assessments} assessments")
    
    except Exception as e:
        print(f"   ✗ Error during migration: {e}")
        db.session.rollback()
        return False
    
    # Step 4: Verify migration
    print("\n[4/4] Verifying migration...")
    
    try:
        with app.app_context():
            user_count = User.query.count()
            assessment_count = AssessmentHistory.query.count()
            
            print(f"   ✓ Users in Supabase: {user_count}")
            print(f"   ✓ Assessments in Supabase: {assessment_count}")
    except Exception as e:
        print(f"   ✗ Error verifying: {e}")
        return False
    
    print("\n" + "="*60)
    print("  ✓ MIGRATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Test your app: python src/app.py")
    print("2. Try logging in with a migrated user")
    print("3. Visit http://localhost:5000 in your browser")
    print("4. When deploying, remember to set environment variables:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_KEY")
    print("   - DATABASE_URL")
    print("\nDoc: https://supabase.com/docs")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
