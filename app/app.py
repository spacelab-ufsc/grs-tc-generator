# app/app.py
from flask import Flask
from database.factories.database_manager import DatabaseManager
from database.database_config import Base

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(f'config.{config_name.capitalize()}Config')

    # Initialize database
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    db_type = 'postgresql' if 'postgresql' in db_url else 'sqlite'
    DatabaseManager.init_db(db_type=db_type)

    # Register blueprints, etc.
    # from .routes import main
    # app.register_blueprint(main)

    # Add teardown context
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        DatabaseManager.close_session(None)  # This will close all sessions

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
