from flask import Flask
from.config import Config
from .db import close_db
from .routes.posts import posts_bp
from .routes.comments import comments_bp 

def create_app():
    #create app instance
    app =Flask(__name__)

    #load configurations from config file
    app.config.from_object(Config)

    #register blueprints
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)

    # Teardown: close DB connection after each request
    app.teardown_appcontext(close_db)

    return app

# Create the app instance
# app = create_app()

# # Run the app if this file is executed directly
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
#     # debug=True - Auto-restart on code changes

#     # host='0.0.0.0' - Allow connections from other devices on network

#     # port=5000 - Default Flask port




