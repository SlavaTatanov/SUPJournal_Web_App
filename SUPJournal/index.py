from flask import Blueprint, render_template, g, redirect, url_for, session
import io
from SUPJournal.tools.gpx import GpxFile
from SUPJournal.database.models import Workout
from SUPJournal.tools.cache import cache
from SUPJournal.database.models import User

bp = Blueprint("index", __name__)

@cache.memoize(timeout=120)
def get_user(user_id):
    """
    Если пользователя нет в g, делаем запрос в БД, результат кешируем на 2 минуты,
    чтобы каждый http запрос не делать запрос в БД, а брать его из кеша
    """
    user = User.query.filter_by(user_id=user_id).first()
    print("Запрос в БД")
    return user


@bp.before_app_request
def load_user():
    """
    Смотрим сессию браузера, берем оттуда user_id и по нему делаем запрос в БД
    Если в сессии нет user_id грузим в g.user -> None
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        get_user(user_id)

@bp.route("/")
def index():
    if g.user is None:
        return redirect(url_for("auth.login"))
    return render_template("index.html", user=g.user.login)

@bp.route("/<username>")
def profile(username):
    if g.user is None:
        return redirect(url_for("auth.login"))
    if username == g.user.login:
        return render_template("profile.html", user=g.user.login)

@bp.route("/<username>/trainings")
def trainings(username):
    if g.user is None:
        return redirect(url_for("auth.login"))
    if username == g.user.login:
        owner_trainings = Workout.query.filter_by(owner_id=g.user.user_id).all()
        return render_template("trainings.html", user=g.user.login, trainings=owner_trainings)

@bp.route("/<username>/trainings/<training_id>")
def training(username, training_id):
    if g.user is None:
        return redirect(url_for("auth.login"))
    if username == g.user.login:
        owner_id = g.user.user_id
        owner_training = Workout.query.filter_by(owner_id=owner_id, training_id=training_id).first()
        training_map = owner_training.gpx
        tr = GpxFile(io.BytesIO(training_map))
        return render_template("training.html",
                               tr=tr,
                               map_html=tr.get_root_map(),
                               user=g.user.login)

@bp.route("/<username>/settings")
def user_settings(username):
    if g.user is None:
        return redirect(url_for("auth.login"))
    if username == g.user.login:
        return render_template("settings.html", user=g.user.login)