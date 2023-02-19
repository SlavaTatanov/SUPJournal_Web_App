"""
API для общения мобильного приложения с сервером.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from SUPJournal.database.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from SUPJournal.database.database import db

bp = Blueprint("api_mobile", __name__, url_prefix="/api/mobile")

STATUS = {"incorrect_user": "incorrect_user",
          "incorrect_password": "incorrect_password",
          "ok": "ok",
          "access_denied": "access_denied"}  # Стандартные значения которые сервер отдаст в статусе

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

def create_response(resp: Response):
    """
    Создание JSON для ответа
    """
    return resp.to_json()


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
        return create_response(Response(STATUS["incorrect_user"], msg="Пользователь не существует"))
    elif not check_password_hash(query.pass_, password):
        return create_response(Response(STATUS["incorrect_password"], msg="Неверный пароль"))

    return create_response(Response(STATUS["ok"], token=create_access_token(query.login)))

@bp.route("/register", methods=["POST"])
def mobile_register():
    """
    Регистрация пользователя.
    !! Надо допиливать !!
    """
    login = request.json["user"]
    pass_ = request.json["pass_"]
    e_mail = request.json["e_mail"]

    password = generate_password_hash(pass_)

    user = User(login=login, pass_=password, e_mail=e_mail)
    db.session.add(user)
    db.session.commit()

    return  create_response(Response(STATUS["ok"],
                                     token=create_access_token(login),
                                     msg="Успешная регистрация"))


@bp.route("/check", methods=["GET"])
@jwt_required()
def mobile_check():
    """
    Валидация юзера
    """
    user = get_jwt_identity()
    return create_response(Response(STATUS["ok"], msg=f"Токен валиден для {user}"))

@bp.route("/delete", methods=["DELETE"])
@jwt_required()
def mobile_delete_user():
    """
    Удаление юзера
    """
    user = request.json["user"]
    if user == get_jwt_identity():
        db.session.query(User).filter(User.login == user).delete()
        db.session.commit()
        return create_response(Response(STATUS["ok"], msg=f"Пользователь {user} - удален"))
    return create_response(Response(STATUS["access_denied"], msg=f"Ошибка доступа"))

@bp.route("/change_password", methods=["POST"])
@jwt_required()
def mobile_change_password():
    """
    Смена действующего пароля
    """
    user = request.json["user"]
    password = request.json["password"]
    new_password = request.json["new_password"]

    if user == get_jwt_identity():
        user_query = User.query.filter_by(login=user).first()
        if check_password_hash(user_query.pass_, password):
            user_query.pass_ = generate_password_hash(new_password)
            db.session.commit()
            return create_response(Response(STATUS["ok"], msg="Пароль успешно изменен"))
        elif not check_password_hash(user_query.pass_, password):
            return create_response(Response(STATUS["incorrect_password"], msg="Неверный пароль"))

    return create_response(Response(STATUS["access_denied"], msg="Доступ запрещен"))

@bp.route("/get_training", methods=["GET"])
@jwt_required()
def mobile_get_training():
    """
    Заготовка для получения данных о тренировке по ее id
    """
    training_id = request.args.get("training_id")
    return create_response(Response(status=STATUS["ok"], msg=f"Тренировка {training_id}"))