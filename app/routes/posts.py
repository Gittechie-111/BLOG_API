from flask import Blueprint, jsonify, g
from ..db import get_db

posts_bp=Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/test', methods=['GET'])
def test_posts():
    return jsonify({"message": "Posts Blueprint is working!"})

@posts_bp.route('/db-test', methods=['GET'])
def test_db():
    db = get_db()
    db = get_db()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchall() #This consumes the result set, allowing the cursor to close cleanly.
    cursor.close()
    return jsonify({"message": "Database connection successful!"})
