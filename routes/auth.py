from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.json or {}

    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role     = data.get('role', '').strip()

    
    if not name or not email or not password or not role:
        return jsonify({"message": "All fields are required"}), 400

    
    if role not in ('student', 'company'):
        return jsonify({"message": "Invalid role. Must be student or company"}), 400

    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    
    hashed = generate_password_hash(password)

    user = User(
        name          = name,
        email         = email,
        password_hash = hashed,
        role          = role
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.json or {}

    email    = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"message": "Account deactivated. Contact admin."}), 403

    
    session['user_id'] = user.id
    session['role']    = user.role

    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "role":    user.role,
        "name":    user.name
    }), 200


@auth.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200
