from flask import Blueprint, jsonify, g, request
from ..db import get_db
from .posts import fetch_post

comments_bp=Blueprint('comments', __name__, url_prefix='/posts/<int:post_id>/comments')

@comments_bp.route('/test', methods=['GET'])
def test_comments():
    return jsonify({"message": "Comments blueprint test OK"})

#helper to check if post exists
def post_exists(post_id):
    return fetch_post(post_id) is not None #calling the helper function

#get all comments
@comments_bp.route('/', methods=['GET'])
def get_comments(post_id):
    if not post_exists(post_id):
        return jsonify({'error' : 'Post not found'}), 404
    
    db= get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM comments WHERE post_id=%s ORDER BY created_at ASC", (post_id,))
    comments = cursor.fetchall()
    cursor.close()
    return jsonify(comments)

#posting/creating a new comment
@comments_bp.route('/', methods=['POST'])
def create_comment(post_id):
    if not post_exists(post_id):
        return jsonify({'error' : 'Post not found'}), 404
    
    data = request.get_json()
    #validate input data
    if not data:
        return jsonify({'error' : 'No data input provided'}), 400
    if 'author' not in data:
        return jsonify({'error' : 'Author not provided'}), 400
    if 'content' not in data:
        return jsonify({'error' : 'Content not provided'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO comments (post_id, author, content) VALUES (%s, %s, %s)", 
                   (post_id, data['author'], data['content']))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()

    #fetch and return new comment
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM comments WHERE id=%s", (new_id,))
    new_comment = cursor.fetchone()
    cursor.close()
    return jsonify(new_comment), 201
    

print("Comments blueprint loaded")
    
