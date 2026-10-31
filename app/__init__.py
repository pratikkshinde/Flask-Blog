import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, int(user_id))


def create_app(config_name=None):
    """Application factory for creating Flask app instances."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.blog import blog_bp
    from app.blueprints.errors import errors_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/posts')
    app.register_blueprint(errors_bp)

    # Serverless / Vercel path normalization middleware
    class VercelPathFixMiddleware:
        def __init__(self, wsgi_app):
            self.wsgi_app = wsgi_app

        def __call__(self, environ, start_response):
            path_info = environ.get('PATH_INFO', '')
            if path_info in ('/api/index', '/api', '/api/'):
                environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[10:]
            elif path_info.startswith('/api/'):
                environ['PATH_INFO'] = path_info[4:]
            environ['SCRIPT_NAME'] = ''
            return self.wsgi_app(environ, start_response)

    app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

    # Redirect Render traffic automatically to Vercel
    @app.before_request
    def redirect_render_to_vercel():
        from flask import request, redirect
        host = request.host.lower()
        if 'onrender.com' in host:
            qs = request.query_string.decode('utf-8') if request.query_string else ''
            target = f"https://blogify-ps.vercel.app{request.path}"
            if qs:
                target = f"{target}?{qs}"
            return redirect(target, code=301)

    # Context processors for global template access
    from app.models import Category
    from app.forms import SearchForm

    @app.context_processor
    def inject_global_template_data():
        try:
            categories = Category.query.order_by(Category.name.asc()).all()
        except Exception:
            categories = []

        def get_csrf():
            try:
                return generate_csrf()
            except Exception:
                return ''

        return {
            'global_categories': categories,
            'search_form': SearchForm(),
            'csrf_token': get_csrf
        }

    return app
