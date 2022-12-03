from flask import Flask


def create_app():
    app = Flask(__name__)
    from . import auth, training
    app.register_blueprint(auth.bp)
    app.register_blueprint(training.bp)
    return app
