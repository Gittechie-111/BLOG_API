from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import timedelta
from ..db import get_db

#create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth' )
#store bcrypt variable
bcrypt = Bcrypt()

#REGISTERING/CREATING A NEW USER
#routing:read json data
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not isinstance(data,dict):
        return jsonify({'error' : 'Invalid JSON or No data provided'}), 400
#validate user credentials
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password are required!'}), 400

#get db connection
    db = get_db()
    cursor = db.cursor()
#check if username or email already exists
    cursor.execute("SELECT id FROM users WHERE username=%s or email=%s", (username, email))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        return jsonify({'error' : 'username or email already exists!'}), 400
#hash password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
#insert values into users(sql query)
    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)" ,(username, email, password_hash))
#commit, get latest id and close cursor
    db.commit()
    user_id = cursor.lastrowid
    cursor.close()
#return message
    return jsonify({'message' : 'User created successfully!', 'user_id' : user_id}), 201


#LOGING IN A USER
@auth_bp.route('/login', methods=['POST'])
def login():
    #read json body
    data = request.get_json()
    if not data:
        return jsonify({'error' : 'No input data provided!'}), 400
#validate user credentials
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error' : 'Username and password are required!'}), 400

#get db connection
    db = get_db()
    # Use dictionary cursor to access columns by name
    cursor = db.cursor(dictionary=True)
#execute query
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username=%s", (username,))
#fetch user
    user = cursor.fetchone()
#close cursor
    cursor.close()
#validate username and password
    if not user or not bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({'error' : 'Invalid username or password!'}), 401
#create JWT token
    access_token = create_access_token(identity=str(user['id']))
    refresh_token = create_refresh_token(identity=str(user['id']))
    return jsonify({
        'access_token' : access_token, 'user_id' : user['id'],
        'refresh_token' : refresh_token, 'user_id' : user['id'],
        'user_id' : user['id']
        }), 200


#refreshing access token
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)

def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({'access_token' : new_access_token}), 200

#Important: The client must send the refresh token in the Authorization header as Bearer <refresh_token>.