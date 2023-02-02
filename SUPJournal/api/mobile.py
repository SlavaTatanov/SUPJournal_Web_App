from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import create_access_token
from flask import request
from SUPJournal.database.models import User
from werkzeug.security import check_password_hash

bp = Blueprint("api_mobile", __name__, url_prefix="/api/mobile")


@bp.route("/auth", methods=["POST"])
def mobile_auth():
    user = request.json['user']
    password = request.json['pass_']

    query = User.query.filter_by(login=user).first()
    if query is None:
        return "Пользователь не существует"
    elif not check_password_hash(query.pass_, password):
        return "Неверный пароль"

    return jsonify(token=create_access_token(query.login))
