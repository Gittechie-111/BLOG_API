from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Hardcoded list of posts (temporary)
posts = [
    {'id': 1, 'title': 'First Post', 'content': 'Hello world!', 'created_at': '2025-03-01'},
    {'id': 2, 'title': 'Second Post', 'content': 'Another post', 'created_at': '2025-03-02'}
]

class Post(db.model):
    ___tablename__ ='posts'


















@app.route('/posts', methods=['GET'])
def get_posts():
    return jsonify(posts)

# Test route
@app.route('/')
def home():
    return "Blog API is running!"

# Optional: test database connection
@app.route('/test-db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"message": "Database connection successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)