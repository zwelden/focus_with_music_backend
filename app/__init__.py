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

    return app


from app import models