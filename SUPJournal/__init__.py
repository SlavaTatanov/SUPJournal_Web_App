from flask import Flask
from SUPJournal.database.database import db, URI
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = URI
    app.config["JWT_SECRET_KEY"] = "dev"
    JWTManager(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from . import auth, training, index
    app.register_blueprint(auth.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(index.bp)
    from SUPJournal.api import mobile
    app.register_blueprint(mobile.bp)
    return app
