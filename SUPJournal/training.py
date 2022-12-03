from flask import Blueprint, render_template

bp = Blueprint("training", __name__)

@bp.route("/training", methods=("GET", "POST"))
def training():
    return render_template("training.html")

@bp.route("/map", methods=("GET", "POST"))
def map_rend():
    return render_template("map.html")