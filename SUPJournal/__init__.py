from flask import Flask
from SUPJournal.database.database import db, URI


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = URI
    db.init_app(app)
    with app.app_context():
        db.create_all()


    from . import auth, training, index
    app.register_blueprint(auth.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(index.bp)
    return app
