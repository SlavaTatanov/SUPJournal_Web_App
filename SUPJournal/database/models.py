from SUPJournal.database.database import db


class User(db.Model):
    """
    Основные данные аккаунта, id, имя аккаунта,хеш пароля, почта
    """
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False, unique=True)
    pass_ = db.Column(db.Text, nullable=False)
    e_mail = db.Column(db.Text, nullable=False, unique=True)

    workouts = db.relationship('Workout', backref='owner', cascade="all, delete-orphan")


class UserData(db.Model):
    """
    Абстрактный класс реализующий базу для пользовательских классов (Тренировки, Оборудование)
    Содержит id как primary key и owner_id как id владельца
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)


class Equipment(UserData):
    """
    Абстрактный класс реализующий базу для пользовательского оборудования (САП, весло)
    """
    __abstract__ = True

    manufacturer = db.Column(db.String, nullable=True)
    model_name = db.Column(db.String, nullable=True)
    km = db.Column(db.Float)


class Workout(UserData):
    """
    Тренировка пользователя которая содержит GPX файл
    """
    __tablename__ = "workout"

    date = db.Column(db.DateTime, nullable=False)
    dist = db.Column(db.String(64), nullable=False)
    tr_time = db.Column(db.Interval, nullable=False)
    gpx = db.Column(db.LargeBinary, nullable=False)


class SupBoard(Equipment):
    """
    САП-борд пользователя
    """
    __tablename__ = "sup_boards"

    width = db.Column(db.Float)
    length = db.Column(db.Float)


class Paddle(Equipment):
    __tablename__ = "paddle"


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    profile_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
