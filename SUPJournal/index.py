from flask import Blueprint, render_template, g, redirect, url_for, session
import io
from SUPJournal.tools.gpx import GpxFile
from SUPJournal.database.models import Workout

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
        owner_trainings = Workout.query.filter_by(owner_id=g.user.user_id).all()
        return render_template("trainings.html", user=g.user.login, trainings=owner_trainings)

@bp.route("/<username>/trainings/<training_id>")
def training(username, training_id):
    if username == g.user.login:
        owner_id = g.user.user_id
        owner_training = Workout.query.filter_by(owner_id=owner_id, training_id=training_id).first()
        training_map = owner_training.gpx
        tr = GpxFile(io.BytesIO(training_map))
        return render_template("training.html", dst=tr.dist, tm=tr.time, map_html=tr.get_root_map(), user=g.user.login)