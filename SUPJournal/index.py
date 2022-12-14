from flask import Blueprint, render_template, g

bp = Blueprint("index", __name__)

@bp.route("/")
def index():
    return render_template("index.html", user=g.user["login"])