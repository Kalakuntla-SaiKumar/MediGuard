"""
Authentication Routes
Handles user login, registration, and logout
Supports both SQLite and Supabase
"""

import os
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash
import logging
import requests

# Choose auth backend based on environment
USE_SUPABASE = os.getenv('SUPABASE_URL') is not None

if USE_SUPABASE:
    from src.supabase_config import db
    from src.supabase_models import User, AssessmentHistory
else:
    from src.models import db, User, AssessmentHistory

from src.mail_utils import send_password_reset_email, send_welcome_email

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api')


# ============================================
# REGISTER ENDPOINT
# ============================================

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        age = data.get('age')
        health_conditions = data.get('health_conditions', '').strip()
        allergies = data.get('allergies', '').strip()
        security_answer_1 = data.get('security_answer_1', '').strip()
        security_answer_2 = data.get('security_answer_2', '').strip()
        
        if not email or not username or not password:
            return jsonify({"error": "Email, username, and password are required"}), 400
        
        if not security_answer_1 or not security_answer_2:
            return jsonify({"error": "Security question answers are required"}), 400
        
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409
        
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        
        try:
            user = User(
                email=email,
                username=username,
                age=age if age else None,
                health_conditions=health_conditions if health_conditions else None,
                allergies=allergies if allergies else None,
                security_question_1="What city were you born in?",
                security_question_2="What is your favorite color?"
            )
            user.set_password(password)
            user.set_security_answers(security_answer_1, security_answer_2)
            
            db.session.add(user)
            db.session.commit()
            
            try:
                mail = current_app.extensions.get('mail')
                if mail:
                    send_welcome_email(mail, user.email, user.username)
            except Exception as email_error:
                logger.error(f"✗ Failed to send welcome email: {str(email_error)}")
            
            logger.info(f"✓ User registered: {username}")
            
            return jsonify({
                "status": "success",
                "message": "Account created successfully",
                "user": user.to_dict()
            }), 201
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        logger.error(f"✗ Registration error: {str(e)}")
        return jsonify({"error": "Registration failed"}), 500


# ============================================
# LOGIN ENDPOINT
# ============================================

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        user = User.query.filter_by(email=email).first()

        password_ok = False
        if user:
            try:
                password_ok = user.check_password(password)
            except Exception as check_err:
                # Support legacy rows that may store plaintext passwords.
                logger.warning(f"Password hash check failed for {email}: {str(check_err)}")
                stored = (getattr(user, 'password_hash', '') or '').strip()
                if stored and stored == password:
                    user.set_password(password)
                    db.session.commit()
                    password_ok = True

        if not user or not password_ok:
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account is inactive"}), 403
        
        # Supabase user IDs are UUIDs; keep session values JSON-serializable.
        session['user_id'] = str(user.id)
        session['username'] = str(user.username)
        session.permanent = True
        
        logger.info(f"✓ User logged in: {user.username}")
        
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


# ============================================
# LOGOUT ENDPOINT
# ============================================

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        username = session.get('username', 'User')
        session.clear()
        logger.info(f"✓ User logged out: {username}")
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200
    except Exception as e:
        logger.error(f"✗ Logout error: {str(e)}")
        return jsonify({"error": "Logout failed"}), 500


# ============================================
# GET CURRENT USER
# ============================================

@auth_bp.route('/user', methods=['GET'])
def get_current_user():
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401
        
        user = User.query.get(user_id)
        
        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "status": "success",
            "user": user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Get user error: {str(e)}")
        return jsonify({"error": "Failed to get user"}), 500


# ============================================
# UPDATE USER PROFILE
# ============================================

@auth_bp.route('/user', methods=['POST'])
def update_user():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401
 
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
 
        data = request.get_json()
 
        # Personal info
        if 'full_name' in data:         user.full_name = data['full_name']
        if 'age' in data:               user.age = data['age']
        if 'gender' in data:            user.gender = data['gender']
        if 'weight' in data:            user.weight = data['weight']
        if 'blood_group' in data:       user.blood_group = data['blood_group']
        if 'phone' in data:             user.phone = data['phone']
 
        # Medical info
        if 'health_conditions' in data: user.health_conditions = data['health_conditions']
        if 'allergies' in data:         user.allergies = data['allergies']
        if 'medications' in data:       user.medications = data['medications']
        if 'pregnancy_status' in data:  user.pregnancy_status = data['pregnancy_status']
 
        # Security answers
        if 'security_answer_1' in data and data['security_answer_1']:
            user.security_answer_1 = generate_password_hash(data['security_answer_1'].lower().strip())
        if 'security_answer_2' in data and data['security_answer_2']:
            user.security_answer_2 = generate_password_hash(data['security_answer_2'].lower().strip())
 
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Profile updated",
            "user": user.to_dict()
        }), 200
 
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============================================
# ASSESSMENT HISTORY ENDPOINTS
# ============================================

@auth_bp.route('/assessments', methods=['GET'])
def get_assessments():
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401
        
        assessments = AssessmentHistory.query.filter_by(
            user_id=user_id
        ).order_by(AssessmentHistory.created_at.desc()).all()
        
        return jsonify({
            "status": "success",
            "assessments": [a.to_dict() for a in assessments]
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Get assessments error: {str(e)}")
        return jsonify({"error": "Failed to get assessments"}), 500


# ============================================
# ✅ FIXED: Save assessment - now reads from request body
# ============================================

@auth_bp.route('/assessments', methods=['POST'])
def save_assessment():
    """Save assessment to user history - called from frontend after each check"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        assessment = AssessmentHistory(
            user_id=user_id,
            drug1=data.get('drug1', ''),
            drug2=data.get('drug2', ''),
            condition=data.get('condition', ''),
            ddi_risk=data.get('ddi_risk', 'None'),
            dfi_risk_drug1=data.get('dfi_risk_drug1', 'None'),
            dfi_risk_drug2=data.get('dfi_risk_drug2', 'None'),
            dci_risk_drug1=data.get('dci_risk_drug1', 'None'),
            dci_risk_drug2=data.get('dci_risk_drug2', 'None'),
            overall_risk=data.get('overall_risk', 'None')
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        logger.info(f"✓ Assessment saved for user_id: {user_id}")
        
        return jsonify({"status": "success", "message": "Assessment saved"}), 201
    
    except Exception as e:
        logger.error(f"✗ Save assessment error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to save assessment"}), 500


# ============================================
# PASSWORD RESET ENDPOINTS
# ============================================

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                "message": "Please answer the security questions",
                "security_question_1": "What city were you born in?",
                "security_question_2": "What is your favorite color?"
            }), 200
        
        return jsonify({
            "message": "Please answer the security questions to reset your password",
            "security_question_1": user.security_question_1,
            "security_question_2": user.security_question_2,
            "found": True
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Forgot password error: {str(e)}")
        return jsonify({"error": "Password reset request failed"}), 500


@auth_bp.route('/verify-security-questions', methods=['POST'])
def verify_security_questions():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        answer1 = data.get('security_answer_1', '').strip()
        answer2 = data.get('security_answer_2', '').strip()
        
        if not email or not answer1 or not answer2:
            return jsonify({"error": "Email and both answers are required"}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "Invalid email or security answers"}), 401
        
        if not user.verify_security_answers(answer1, answer2):
            return jsonify({"error": "Incorrect answers to security questions"}), 401
        
        reset_token = user.generate_reset_token()
        db.session.commit()
        
        logger.info(f"✓ Security questions verified for: {email}")
        
        return jsonify({
            "message": "Security answers verified successfully",
            "reset_token": reset_token,
            "success": True
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Security question verification error: {str(e)}")
        return jsonify({"error": "Verification failed"}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        reset_token = data.get('reset_token', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not all([email, reset_token, new_password]):
            return jsonify({"error": "Email, token, and password required"}), 400
        
        if len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if not user.verify_reset_token(reset_token):
            return jsonify({"error": "Invalid or expired reset token"}), 400
        
        user.set_password(new_password)
        user.clear_reset_token()
        db.session.commit()
        
        logger.info(f"✓ Password reset completed for: {user.email}")
        
        return jsonify({
            "message": "Password reset successful",
            "redirect": "/login"
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"✗ Reset password error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Password reset failed"}), 500


# ============================================
# GOOGLE OAUTH ENDPOINTS
# ============================================

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        google_user_info = data.get('user_info', {})
        
        if not google_user_info.get('id'):
            return jsonify({"error": "Invalid Google user data"}), 400
        
        google_id = google_user_info.get('id')
        email = google_user_info.get('email', '').strip()
        
        if not email:
            return jsonify({"error": "Google email required"}), 400
        
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                username = email.split('@')[0]
                counter = 1
                original_username = username
                while User.query.filter_by(username=username).first():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User(
                    email=email,
                    username=username,
                    google_id=google_id,
                    google_email=email,
                    auth_method='google',
                    is_active=True
                )
                user.password_hash = 'google_oauth'
                db.session.add(user)
            else:
                user.google_id = google_id
                user.google_email = email
                if user.auth_method == 'email':
                    user.auth_method = 'both'
        
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True
        
        logger.info(f"✓ Google login successful: {user.email}")
        
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Google login error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Google login failed"}), 500


@auth_bp.route('/check-google-user', methods=['POST'])
def check_google_user():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"exists": False, "message": "Email not registered"}), 200
        
        return jsonify({
            "exists": True,
            "auth_method": user.auth_method,
            "username": user.username
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Check Google user error: {str(e)}")
        return jsonify({"error": "Check failed"}), 500
    # ============================================
# ADD THIS ROUTE TO src/auth.py
# ============================================

@auth_bp.route('/dfi', methods=['POST'])
def drug_food_interaction():
    """Get drug-food interaction details from dataset"""
    try:
        data = request.get_json()
        drug = data.get('drug', '').strip()

        if not drug:
            return jsonify({"error": "Drug name required"}), 400

        from src.engine.drug_mapper import normalize_drug_lower
        from src.dfi.dfi_module import get_drug_food_details

        drug_norm = normalize_drug_lower(drug)
        result = get_drug_food_details(drug_norm)

        return jsonify({
            "status": "success",
            "drug": drug,
            "drug_mapped": drug_norm,
            "risk": result["risk"],
            "interactions": result["interactions"]
        }), 200

    except Exception as e:
        logger.error(f"DFI error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
# ============================================
# REPLACE your delete routes in src/auth.py with these
# Make sure AssessmentHistory is imported at top of auth.py:
# from src.models import db, User, AssessmentHistory
# ============================================

@auth_bp.route('/assessments/clear', methods=['DELETE'])
def clear_assessments():
    """Delete ALL assessments for current user"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        AssessmentHistory.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
        return jsonify({"status": "cleared"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/assessments/<int:assessment_id>', methods=['DELETE'])
def delete_assessment(assessment_id):
    """Delete a single assessment"""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        assessment = AssessmentHistory.query.filter_by(
            id=assessment_id,
            user_id=session['user_id']
        ).first()
        if not assessment:
            return jsonify({"error": "Assessment not found"}), 404
        db.session.delete(assessment)
        db.session.commit()
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/foods', methods=['GET'])
def get_food_list():
    """Serve food list from extracted dataset"""
    import json
    try:
        food_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  'data', 'processed', 'food_list.json')
        with open(food_path, 'r') as f:
            foods = json.load(f)
        return jsonify({"status": "success", "foods": foods, "count": len(foods)}), 200
    except FileNotFoundError:
        return jsonify({"status": "error", "foods": [], "message": "food_list.json not found"}), 200


@auth_bp.route('/drugs', methods=['GET'])
def get_drug_list():
    """Serve full drug list from ML encoder + brand names"""
    try:
        import pickle
        import os

        encoder_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'models', 'drug_label_encoder.pkl'
        )
        import joblib
        encoder = joblib.load(encoder_path)

        # Get encoder drugs (Title Case generic names)
        encoder_drugs = sorted(encoder.classes_.tolist())

        # Add brand names / Indian names
        brand_names = [
            'dolo', 'crocin', 'calpol', 'tylenol', 'panadol', 'febrex',
            'brufen', 'combiflam', 'advil', 'ecosprin', 'disprin',
            'glycomet', 'glucophage', 'lipitor', 'atorva', 'norvasc',
            'amlip', 'omez', 'pan', 'pantop', 'azee', 'azithral',
            'cipro', 'ciplox', 'coumadin', 'warf', 'valium', 'wysolone',
            'decadron', 'cozaar', 'losar', 'betaloc', 'zocor', 'neurontin',
            'gabapin', 'zoloft', 'serta', 'prozac', 'fludac', 'plavix',
            'clopilet', 'synthroid', 'eltroxin', 'thyronorm', 'lasix',
            'frusemide', 'lanoxin', 'cardace', 'aldactone', 'rheumatrex',
            'folitrax', 'neoral', 'prograf', 'seroquel', 'risperdal',
            'xanax', 'alprax', 'ativan', 'lamictal', 'lamitor', 'depakote',
            'valparin', 'capoten', 'ultram', 'paracetamol', 'acetaminophen',
            'ibuprofen', 'warfarin', 'aspirin', 'metformin', 'amoxicillin'
        ]

        all_drugs = sorted(list(set(encoder_drugs + brand_names)))
        return jsonify({"status": "success", "drugs": all_drugs, "count": len(all_drugs)}), 200
    except Exception as e:
        return jsonify({"status": "error", "drugs": [], "message": str(e)}), 200
 
@auth_bp.route('/config', methods=['GET'])
def get_config():
    """Serve non-sensitive config to authenticated users"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "groq_key": os.environ.get('GROQ_API_KEY', '')
    }), 200


@auth_bp.route('/chat-completions', methods=['POST'])
def chat_completions():
    """Proxy chat-completions to Groq using server-side API key."""
    try:
        groq_key = os.getenv('GROQ_API_KEY') or os.getenv('GROQ_KEY')
        if not groq_key:
            return jsonify({"error": "Groq API key is not configured on server"}), 500

        data = request.get_json() or {}
        messages = data.get('messages')
        if not isinstance(messages, list) or not messages:
            return jsonify({"error": "messages array is required"}), 400

        payload = {
            "model": data.get('model', 'llama-3.3-70b-versatile'),
            "messages": messages,
            "max_tokens": int(data.get('max_tokens', 1024)),
            "temperature": float(data.get('temperature', 0.4)),
        }

        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {groq_key}'
            },
            json=payload,
            timeout=45,
        )

        return jsonify(resp.json()), resp.status_code

    except requests.RequestException as e:
        logger.error(f"✗ Groq request error: {str(e)}")
        return jsonify({"error": "Failed to connect to Groq service"}), 502
    except Exception as e:
        logger.error(f"✗ Chat proxy error: {str(e)}")
        return jsonify({"error": "Chat proxy failed"}), 500

 
@auth_bp.route('/dfi/lookup', methods=['POST'])
def dfi_lookup():
    """Check specific drug+food pair in curated lookup table"""
    import json
    try:
        data = request.get_json()
        drug = data.get('drug', '').strip().lower()
        food = data.get('food', '').strip().lower()
 
        if not drug or not food:
            return jsonify({"found": False}), 200
 
        lookup_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'processed', 'drug_food_lookup.json'
        )
 
        with open(lookup_path, 'r') as f:
            lookup = json.load(f)
 
        # Try both directions
        from src.engine.drug_mapper import normalize_drug_lower
        drug_norm = normalize_drug_lower(drug)
        food_norm = food.strip().lower()
 
        key1 = f"{drug_norm}+{food_norm}"
        key2 = f"{drug}+{food_norm}"
        key3 = f"{food_norm}+{drug_norm}"
 
        result = lookup.get(key1) or lookup.get(key2) or lookup.get(key3)
 
        if result:
            return jsonify({
                "found": True,
                "risk": result["risk"],
                "mechanism": result["mechanism"]
            }), 200
        else:
            return jsonify({"found": False}), 200
 
    except Exception as e:
        return jsonify({"found": False, "error": str(e)}), 200
 