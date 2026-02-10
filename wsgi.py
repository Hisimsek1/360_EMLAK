"""
WSGI Entry Point for 360 Emlak Platform
Used for production deployment with WSGI servers like Gunicorn
"""
import os
from app import create_app

# Get environment from environment variable, default to development
env = os.environ.get('FLASK_ENV', 'development')

# Create the Flask application
app = create_app(env)

if __name__ == "__main__":
    # This block is for development only
    # In production, use: gunicorn wsgi:app
    app.run(host='0.0.0.0', port=5000)
