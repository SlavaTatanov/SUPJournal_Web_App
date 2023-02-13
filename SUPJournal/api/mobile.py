"""
API для общения мобильного приложения с сервером.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from SUPJournal.database.models import User
from werkzeug.security import check_password_hash

bp = Blueprint("api_mobile", __name__, url_prefix="/api/mobile")

STATUS = {"incorrect_user": "incorrect_user",
             "incorrect_password": "incorrect_password",
             "ok": "ok"}  # Стандартные значения которые сервер отдаст в статусе

class Response:
    """
    Интерфейс ответа сервера для мобильного API. Указывает допустимые поля в ответе.
    При создании объекта для его отправки применяется метод to_json.
    """
    def __init__(self, status: str, token: str = "", msg: str = ""):
        self.status = status
        self.token = token
        self.msg = msg

    def to_json(self):
        """
        Формирует JSON для отправки.
        Укладывает в тело ответа только заполненные поля.
        """
        body = {k: v for k, v in self.__dict__.items() if v}
        return jsonify(**body)


@bp.route("/auth", methods=["POST"])
def mobile_auth():
    """
    Авторизация пользователя.
    Принимаем запрос с пользователем паролем, проверяем данные.
    Если ок -> отдаем JWT токен.
    Если не ок -> говорим пользователю, что пошло не так.
    """
    user = request.json['user']
    password = request.json['pass_']

    query = User.query.filter_by(login=user).first()
    if query is None:
        return Response(STATUS["incorrect_user"], msg="Пользователь не существует").to_json()
    elif not check_password_hash(query.pass_, password):
        return Response(STATUS["incorrect_password"], msg="Неверный пароль").to_json()

    return Response(STATUS["ok"], token=create_access_token(query.login)).to_json()

@bp.route("/check", methods=["GET"])
@jwt_required()
def mobile_check():
    """
    Валидация юзера
    """
    return Response(STATUS["ok"], msg="Токен валиден").to_json()
