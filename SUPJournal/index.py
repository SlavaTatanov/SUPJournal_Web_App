from flask import Blueprint, render_template, g, redirect, url_for, session

from SUPJournal.database.models import User

bp = Blueprint("index", __name__)

@bp.before_app_request
def load_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(user_id=user_id).first()

@bp.route("/")
def index():
    if g.user is None:
        return redirect(url_for("auth.login"))
    return render_template("index.html", user=g.user.login)

@bp.route("/<username>")
def profile(username):
    if username == g.user.login:
        return render_template("profile.html", user=g.user.login)

@bp.route("/<username>/trainings")
def trainings(username):
    if username == g.user.login:
        return "Тренировки тут"