from flask import Blueprint
from flask import jsonify
from flask_jwt_extended import create_access_token
from flask import request
from SUPJournal.database.models import User
from werkzeug.security import check_password_hash

bp = Blueprint("api_mobile", __name__, url_prefix="/api/mobile")

class Response:
    def __init__(self, status: str, token: str = "", msg: str = ""):
        self.status = status
        self.token = token
        self.msg = msg

    def to_json(self):
        return jsonify(status=self.status, token=self.token, msg=self.msg)


@bp.route("/auth", methods=["POST"])
def mobile_auth():
    user = request.json['user']
    password = request.json['pass_']

    query = User.query.filter_by(login=user).first()
    if query is None:
        return Response("false", msg="Пользователь не существует").to_json()
    elif not check_password_hash(query.pass_, password):
        return Response("false", msg="Неверный пароль").to_json()

    return Response("ok", create_access_token(query.login)).to_json()
