"""
360 Emlak Platform - Main Application Factory
Professional SaaS Real Estate Platform with Flask
"""
import os
import logging
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import get_config


# Initialize Flask extensions (without app binding)
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """
    Application Factory Pattern
    Creates and configures the Flask application instance
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
    
    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATA_FILE']), exist_ok=True)
    
    # Configure logging
    setup_logging(app)
    
    # Initialize extensions with app
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters and context processors
    register_template_utilities(app)
    
    app.logger.info(f"360 Emlak Platform started in {config_name} mode")
    
    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists(app.config['LOG_FOLDER']):
            os.makedirs(app.config['LOG_FOLDER'])
        
        file_handler = logging.FileHandler(app.config['LOG_FILE'], encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    else:
        # Development logging (console)
        app.logger.setLevel(logging.DEBUG)


def init_extensions(app):
    """Initialize Flask extensions"""
    
    # CSRF Protection
    csrf.init_app(app)
    
    # Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfayı görüntülemek için lütfen giriş yapın.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        """Load user from data store"""
        from core.data_manager import get_data_manager
        from core.models import User
        
        dm = get_data_manager()
        user_data = dm.find_one('users', lambda u: u['id'] == user_id)
        
        if user_data:
            return User(user_data)
        return None


def register_blueprints(app):
    """Register application blueprints"""
    
    # Import blueprints
    from blueprints.main.routes import main_bp
    from blueprints.auth.routes import auth_bp
    from blueprints.dashboard.routes import dashboard_bp
    from blueprints.property.routes import property_bp
    from blueprints.tour.routes import tour_bp
    from blueprints.api import api_bp
    from blueprints.admin.routes import admin_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(property_bp, url_prefix='/property')
    app.register_blueprint(tour_bp, url_prefix='/tour')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Exempt tour API routes from CSRF
    csrf.exempt(tour_bp)


def register_error_handlers(app):
    """Register custom error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file upload size errors"""
        return render_template('errors/413.html'), 413


def register_template_utilities(app):
    """Register template filters and context processors"""
    
    from datetime import datetime
    
    @app.template_filter('format_date')
    def format_date(date_string):
        """Format date string for display"""
        try:
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.strftime('%d.%m.%Y')
        except:
            return date_string
    
    @app.template_filter('format_datetime')
    def format_datetime(date_string):
        """Format datetime string for display"""
        try:
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.strftime('%d.%m.%Y %H:%M')
        except:
            return date_string
    
    @app.template_filter('format_price')
    def format_price(price):
        """Format price with thousand separators"""
        try:
            return f"{int(price):,}".replace(',', '.')
        except:
            return price
    
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates"""
        return {
            'app_name': app.config.get('APP_NAME', '360 Emlak'),
            'primary_color': app.config.get('PRIMARY_COLOR', '#00A8E8'),
            'current_year': datetime.now().year
        }


if __name__ == '__main__':
    # For development only
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
