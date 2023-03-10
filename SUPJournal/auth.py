from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from SUPJournal.database.database import db
from SUPJournal.database.models import User
from sqlalchemy import exc

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.before_app_request
def load_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(user_id=user_id).first()

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        error = None
        username = request.form["username"]
        password = request.form["password"]
        rep_password = request.form["rep_password"]
        e_mail = request.form["e-mail"]

        if not  username:
            error = "Введите логин"
        elif not password:
            error = "Введите пароль"
        elif password != rep_password:
            error = "Пароли не совпадают"

        if error is None:
            try:
                password = generate_password_hash(password)
                user = User(login=username, pass_=password, e_mail=e_mail)
                db.session.add(user)  # Реализация от Flask-SQLAlchemy (см. док)
                db.session.commit()
                return redirect(url_for("auth.login"))
            except exc.IntegrityError:
                error = "Такой пользователь уже существует"
        flash(error)
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        user_login = request.form["login"]
        password = request.form["password"]
        error = None

        query = User.query.filter_by(login=user_login).first()

        if query is None:
            error = f"Пользователь {user_login} не существует"
        elif not check_password_hash(query.pass_, password):
            error = "Неверный пароль"

        if not error:
            session.clear()
            session["user_id"] = query.user_id
            return redirect(url_for("index.index"))

        flash(error)
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))