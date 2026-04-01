from flask import Blueprint, jsonify, g, request
from ..db import get_db
from .posts import fetch_post
from flask_jwt_extended import jwt_required, get_jwt_identity

comments_bp=Blueprint('comments', __name__, url_prefix='/posts/<int:post_id>/comments')

#helper function to fetch one comment
def fetch_comment(comment_id, post_id=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if post_id:
        cursor.execute("SELECT * FROM comments WHERE id=%s AND post_id=%s", (comment_id, post_id,))
    else:
        cursor.execute("SELECT * FROM comments WHERE comment_id=%s", (comment_id,))
    comment = cursor.fetchone()
    cursor.close()
    return comment

#testing 
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
@jwt_required()
def create_comment(post_id):
    user_id = get_jwt_identity()
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
    
#updating a comment
@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id, post_id):
    user_id = int(get_jwt_identity())
    #check if comment exists and belongs to a post
    comment = fetch_comment(comment_id, post_id)
    if not comment:
        return jsonify({'error' : 'Comment not found or does not belong to this post'}), 404
    if comment['user_id'] != user_id:
        return jsonify({'error': 'Not authorized to edit this comment'}), 403
    #read json body
    data = request.get_json()

    #validate input data
    if not data:
        return jsonify({'error' : 'Input data not provided'}), 400
    
    #build dynamic update query
    updates = []
    values = []
    if 'author' in data:
        updates.append('author=%s')
        values.append(data['author'])
    if 'content' in data:
        updates.append('content=%s')
        values.append(data['content'])

    if not updates:
        return jsonify({'error' : 'No fields to update'})

    
    #build dynamic update query
    updates = []
    values = []
    if 'author' in data:
        updates.append('author=%s')
        values.append(data['author'])
    if 'content' in data:
        updates.append('content=%s')
        values.append(data['content'])

    if not updates:
        return jsonify({'error' : 'No fields to update'}), 400
   

    #add comment_id to values
    values.append(comment_id) #for id=%s
    values.append(post_id) #for post_id=%s

    #write sql query
    query = f"UPDATE comments SET {', '.join(updates)} WHERE id=%s AND post_id=%s"

    #get db connection
    db = get_db()
    cursor = db.cursor()
    #execute query
    cursor.execute(query, values)
    #commit and close
    db.commit()
    cursor.close()

    #fetch and return updated comment
    updated_comment = fetch_comment(comment_id, post_id)
    return jsonify(updated_comment)

#deleting a comment
@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    user_id = int(get_jwt_identity())
    #check if post/comment exists
    comment = fetch_comment(comment_id, post_id)
    if not comment:
        return jsonify({'error' : 'Comment does not exist or does not belong to that post'}), 404
    if comment['user_id'] != user_id:
        return jsonify({'error': 'Not authorized to delete this comment'}), 403


    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM comments WHERE id=%s AND post_id=%s", (comment_id, post_id))
    db.commit()
    cursor.close()
    return jsonify({'message' : 'Comment deleted successfully!'}), 200
    
    
   







