"""
User Model and Database Configuration
Handles user data storage and authentication
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Initialize database
db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    weight = db.Column(db.Float)
    blood_group = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    medications = db.Column(db.String(1000))
    # Profile information
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))                  # 'male', 'female', 'other'
    pregnancy_status = db.Column(db.String(20))        # 'not_pregnant', 'pregnant', 'breastfeeding', 'na'
    health_conditions = db.Column(db.String(500))      # Comma-separated list
    allergies = db.Column(db.String(500))              # Comma-separated list
    
    # Account management
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Google OAuth
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    google_email = db.Column(db.String(120), nullable=True)
    auth_method = db.Column(db.String(20), default='email', nullable=False)
    
    # Security Questions for Password Recovery
    security_question_1 = db.Column(db.String(255), nullable=True)
    security_answer_1 = db.Column(db.String(255), nullable=True)
    security_question_2 = db.Column(db.String(255), nullable=True)
    security_answer_2 = db.Column(db.String(255), nullable=True)
    
    # Password reset
    reset_token = db.Column(db.String(255), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    password_reset_requested_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_security_answers(self, answer1, answer2):
        self.security_answer_1 = generate_password_hash(answer1.lower().strip())
        self.security_answer_2 = generate_password_hash(answer2.lower().strip())
    
    def verify_security_answers(self, answer1, answer2):
        answer1_normalized = answer1.lower().strip()
        answer2_normalized = answer2.lower().strip()
        match1 = check_password_hash(self.security_answer_1, answer1_normalized)
        match2 = check_password_hash(self.security_answer_2, answer2_normalized)
        return match1 and match2
    
    def to_dict(self):
     return {
        'id': self.id,
        'email': self.email,
        'username': self.username,
        'age': self.age,
        'gender': self.gender,
        'pregnancy_status': self.pregnancy_status,
        'health_conditions': self.health_conditions,
        'allergies': self.allergies,
        'created_at': self.created_at.isoformat(),
        'is_active': self.is_active,
        'auth_method': self.auth_method,
        'full_name': self.full_name,
        'weight': self.weight,
        'blood_group': self.blood_group,
        'phone': self.phone,
        'medications': self.medications,
    }
    def generate_reset_token(self):
        import secrets
        from datetime import timedelta
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        self.password_reset_requested_at = datetime.utcnow()
        return self.reset_token
    
    def verify_reset_token(self, token):
        if self.reset_token != token:
            return False
        if self.reset_token_expiry < datetime.utcnow():
            return False
        return True
    
    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None


class AssessmentHistory(db.Model):
    """Store user medication assessments"""
    __tablename__ = 'assessment_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drug1 = db.Column(db.String(100), nullable=False)
    drug2 = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    
    ddi_risk = db.Column(db.String(20))
    dfi_risk_drug1 = db.Column(db.String(20))
    dfi_risk_drug2 = db.Column(db.String(20))
    dci_risk_drug1 = db.Column(db.String(20))
    dci_risk_drug2 = db.Column(db.String(20))
    overall_risk = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Assessment {self.drug1} + {self.drug2}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'drug1': self.drug1,
            'drug2': self.drug2,
            'condition': self.condition,
            'ddi_risk': self.ddi_risk,
            'dfi_risk_drug1': self.dfi_risk_drug1,
            'dfi_risk_drug2': self.dfi_risk_drug2,
            'dci_risk_drug1': self.dci_risk_drug1,
            'dci_risk_drug2': self.dci_risk_drug2,
            'overall_risk': self.overall_risk,
            'created_at': self.created_at.isoformat()
        }


def init_db(app):
    """Initialize database with Flask app"""
    with app.app_context():
        db.create_all()
        print("✓ Database initialized")