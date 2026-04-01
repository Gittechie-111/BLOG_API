from flask import Blueprint, jsonify, g, request
from ..db import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp=Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/test', methods=['GET'])
def test_posts():
    return jsonify({"message": "Posts Blueprint is working!"})

@posts_bp.route('/db-test', methods=['GET'])
def test_db():
    db = get_db()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchall() #This consumes the result set, allowing the cursor to close cleanly.
    cursor.close()
    return jsonify({"message": "Database connection successful!"})

#helper function to fetch a single post(used in multiple routes)
def fetch_post(post_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    cursor.close()
    return post


#get a single post
@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = fetch_post(post_id)
    if post:
        return jsonify(post)
    return jsonify({"error" : "Post not found"}) , 404

#get all posts
@posts_bp.route('/', methods=['GET'])
def get_posts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    #pagination parameters
    #request.args is a dictionary-like object containing all the query parameters from the URL.
    #By specifying type=int, Flask automatically converts the string to an integer, or raises a 400 Bad Request if the value cannot be converted (e.g., ?limit=abc).
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT %s OFFSET %s", (limit, offset))
    #LIMIT %s restricts the number of rows returned. OFFSET %s tells MySQL how many rows to skip before starting to return results.
    posts = cursor.fetchall()
    cursor.close()

    return jsonify(posts)


#creating a post
@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()           #retruns a string like "3"
    user_id = int(user_id)                # convert to int if your table expects int
    data = request.get_json()

    if not data:
        return jsonify({'error' : "Data not provided"}), 400
    if not 'title':
        return jsonify({'error' : "Title is required"}), 400
    if not 'content':
        return jsonify({'error': 'Content is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s)", (data['title'], data['content'], user_id))
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    # Fetch the newly created post (using dictionary cursor)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts WHERE id = %s", (new_id,))
    new_post = cursor.fetchone()
    cursor.close()
    return jsonify(new_post), 201

#updating a post
@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    #Since post['user_id'] is an integer, the comparison will be int != str, which will be True even if the numeric values match. 
    # So you should convert user_id to int for consistency
    user_id = int(get_jwt_identity())
    #checking if post exists
    post = fetch_post(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 400
    if post['user_id'] != user_id:
        return jsonify({'error': 'Not authorized to edit this post'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error' : 'No input provided'}), 400
    
    #build update query
    updates = []
    values = []

    if 'title' in data:
        updates.append('title=%s')
        values.append(data['title'])

    if 'content' in data:
        updates.append('content=%s')
        values.append(data['content'])

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400
    
    values.append(post_id)
    
    query = f"UPDATE posts SET {', '.join(updates)} WHERE id=%s"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()
    cursor.close()

    updated_post = fetch_post(post_id)
    if updated_post is None:
        return jsonify({'error': 'Post not found after update'}), 500
    return jsonify(updated_post)


#deleting a post
@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = int(get_jwt_identity())
    post = fetch_post(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if post['user_id'] != user_id:
        return jsonify({'error': 'Not authorized to delete this post'}), 403
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM posts WHERE id=%s", (post_id,))
    db.commit()
    affected_rows = cursor.rowcount
    cursor.close()

    if affected_rows == 0:
        return jsonify({'error': 'Post not found'}), 404
    return jsonify({'message': 'Post deleted successfully!'}), 200

