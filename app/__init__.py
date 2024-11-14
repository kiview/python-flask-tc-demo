from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load config from Config class
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here to ensure they're known to SQLAlchemy
    from app.models import FastestLap, RaceWinner  # Add this line
    
    def setup_database():
        with app.app_context():
            app.logger.info("Setting up database...")
            try:
                # Drop all tables and recreate them (only for development!)
                db.drop_all()
                db.create_all()
                app.logger.info("Database tables created successfully!")
            except Exception as e:
                app.logger.error(f"Error setting up database: {str(e)}")
                raise
    
    # Call setup_database immediately
    setup_database()
    
    # Register blueprints after database setup
    from app.routes import main
    app.register_blueprint(main)
    
    return app 