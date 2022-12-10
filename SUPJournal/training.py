from flask import Blueprint, render_template
from SUPJournal.tools.gpx import GpxFile

bp = Blueprint("training", __name__)

@bp.route("/training", methods=("GET", "POST"))
def training():
    tr = GpxFile("SUPJournal/tools/test.gpx")
    tr.save_map("SUPJournal/templates/map.html")
    return render_template("training.html", dst=tr.dist, tm=tr.time)

@bp.route("/map", methods=("GET", "POST"))
def map_rend():
    return render_template("map.html")