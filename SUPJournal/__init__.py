from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev"

    from . import auth, training, index
    app.register_blueprint(auth.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(index.bp)
    return app
