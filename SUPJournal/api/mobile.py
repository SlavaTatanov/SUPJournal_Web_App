from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from SUPJournal.database.models import User
from werkzeug.security import check_password_hash

bp = Blueprint("api_mobile", __name__, url_prefix="/api/mobile")

CONSTANCE = {"incorrect_user": "incorrect_user",
             "incorrect_password": "incorrect_password",
             "ok": "ok"}

class Response:
    """
    Интерфейс ответа сервера на запрос авторизации
    """
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
        return Response(CONSTANCE["incorrect_user"], msg="Пользователь не существует").to_json()
    elif not check_password_hash(query.pass_, password):
        return Response(CONSTANCE["incorrect_password"], msg="Неверный пароль").to_json()

    return Response(CONSTANCE["ok"], token=create_access_token(query.login)).to_json()
