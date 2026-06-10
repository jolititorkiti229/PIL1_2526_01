from flask import Flask, send_from_directory, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO
import os

bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'),
                static_url_path='')
    
    app.config.from_object('backend.config.Config')
    
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)
    socketio.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Enregistrement des blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.users import users_bp
    from backend.routes.mentorat import mentorat_bp
    from backend.routes.messages import messages_bp
    from backend.routes.notifications import notif_bp
    from backend.routes.matching import matching_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(mentorat_bp, url_prefix='/api/mentorat')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(notif_bp, url_prefix='/api/notifications')
    app.register_blueprint(matching_bp, url_prefix='/api/matching')

    # Serve le frontend
    @app.route('/')
    @app.route('/<path:path>')
    def serve_frontend(path=''):
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(os.path.join(frontend_dir, 'pages'), 'index.html')

    return app
