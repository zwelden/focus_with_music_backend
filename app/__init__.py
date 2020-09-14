import os
import logging 
from logging.handlers import RotatingFileHandler
from flask import Flask 
from config import Config 
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extention initialization
    db.init_app(app) 
    migrate.init_app(app, db)

    # Blueprint registration 
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    # app model extention 

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/api.log', maxBytes=10240, backupCount = 10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Starting API')

    return app


from app import models