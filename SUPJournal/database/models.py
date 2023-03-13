from SUPJournal.database.database import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False, unique=True)
    pass_ = db.Column(db.Text, nullable=False)
    e_mail = db.Column(db.Text, nullable=False, unique=True)

    workouts = db.relationship('Workout', backref='owner', cascade="all, delete-orphan")

class Workout(db.Model):
    __tablename__ = "workout"

    training_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    dist = db.Column(db.String(64), nullable=False)
    tr_time = db.Column(db.Interval, nullable=False)
    gpx = db.Column(db.LargeBinary, nullable=False)

class UserProfile(db.Model):
    __tablename__ = "user_profile"

    profile_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)





