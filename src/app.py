"""
MediGuard Flask Application
Main entry point with authentication and assessment endpoints
"""
from dotenv import load_dotenv
load_dotenv()
import sys
import os
from datetime import timedelta

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, redirect, request, jsonify, send_from_directory, session
from flask_cors import CORS
from src.engine.mediguard_engine import mediguard_assess

# Choose between Supabase or SQLite based on environment
USE_SUPABASE = os.getenv('SUPABASE_URL') is not None

if USE_SUPABASE:
    from src.supabase_config import db, init_supabase, get_db_uri, ensure_supabase_schema
    from src.supabase_models import User, AssessmentHistory
else:
    from src.models import db, User, AssessmentHistory

from src.auth import auth_bp

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_PATH = os.path.join(BASE_DIR, "mediguard.db")

# Create Flask app with static folder
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

# ============================================
# CONFIGURATION
# ============================================

# Session configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mediguard-secret-key-2026')  # Use env var in production
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'  # Set True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database configuration
if USE_SUPABASE:
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
        }
        print("✓ Using Supabase (PostgreSQL)")
    except Exception as e:
        print(f"✗ Error configuring Supabase: {e}")
        print("  Falling back to SQLite")
        USE_SUPABASE = False
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    print("✓ Using SQLite")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

if USE_SUPABASE:
    init_supabase()
    with app.app_context():
        ensure_supabase_schema()

cors_origins_env = os.getenv('CORS_ORIGINS', '')
if cors_origins_env.strip():
    cors_origins = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
else:
    cors_origins = ["http://127.0.0.1:5000", "http://localhost:5000"]

CORS(app, supports_credentials=True, origins=cors_origins)

# Register blueprints
app.register_blueprint(auth_bp)

# ============================================
# ROUTES
# ============================================

@app.route("/")
def home():
    """Serve the dashboard - public page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "dashboard.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Dashboard not found"}), 404


@app.route("/login")
def serve_login():
    """Serve login page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "login.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Login page not found"}), 404


@app.route("/register")
def serve_register():
    """Serve registration page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "register.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Register page not found"}), 404


@app.route("/forgot-password")
def serve_forgot_password():
    """Serve forgot password page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "forgot-password.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Forgot password page not found"}), 404

@app.route("/profile")
def serve_profile():
    try:
        with open(os.path.join(FRONTEND_DIR, "profile.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Profile page not found"}), 404

@app.route("/reset-password")
def serve_reset_password():
    """Serve reset password page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "reset-password.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Reset password page not found"}), 404
    
@app.route("/chat")
def serve_chat():
    """Serve AI chatbot page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "chat.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Chat page not found"}), 404
    
@app.route("/assess-page")
def serve_assess_page():
    """Serve dedicated assessment page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "assess-page.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Page not found"}), 404


@app.route("/history-page")
def serve_history_page():
    """Serve full assessment history page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "history-page.html"), "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Page not found"}), 404

@app.route("/assess", methods=["POST"])
def assess():
    """
    Medication safety assessment endpoint
    Can be called by authenticated or unauthenticated users
    """
    try:
        data = request.get_json()

        # Validate input
        required_fields = ["drug1", "drug2", "condition"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": f"{field} is required"
                }), 400

        drug1 = data["drug1"]
        drug2 = data["drug2"]
        condition = data["condition"]

        # Call assessment engine
        result = mediguard_assess(drug1, drug2, condition)

        # Save to history if user is logged in
        user_id = session.get('user_id')
        if user_id:
            try:
                assessment = AssessmentHistory(
                    user_id=user_id,
                    drug1=drug1,
                    drug2=drug2,
                    condition=condition,
                    ddi_risk=result.get('ddi_risk'),
                    dfi_risk_drug1=result.get('dfi_risk_drug1'),
                    dfi_risk_drug2=result.get('dfi_risk_drug2'),
                    dci_risk_drug1=result.get('dci_risk_drug1'),
                    dci_risk_drug2=result.get('dci_risk_drug2'),
                    overall_risk=result.get('overall_risk')
                )
                db.session.add(assessment)
                db.session.commit()
            except Exception as e:
                print(f"Warning: Could not save assessment history: {str(e)}")
                db.session.rollback()

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


# ============================================
# MAIN APPLICATION
# ============================================

def init_db(app):
    """Initialize database with Flask app"""
    with app.app_context():
        try:
            db.create_all()
            db_type = "Supabase (PostgreSQL)" if USE_SUPABASE else "SQLite"
            print(f"✓ Database initialized ({db_type})")
        except Exception as e:
            print(f"✗ Database initialization error: {e}")
            raise

if __name__ == "__main__":
    # Initialize database
    init_db(app)
    print("✓ MediGuard application ready")
    print(f"✓ Frontend: {FRONTEND_DIR}")
    if USE_SUPABASE:
        print(f"✓ Supabase URL: {os.getenv('SUPABASE_URL', 'Not set').split('.supabase.co')[0] + '...'}")
    else:
        print(f"✓ Database: {DB_PATH}")
    
    # Run Flask
    app.run(debug=True, port=5000)