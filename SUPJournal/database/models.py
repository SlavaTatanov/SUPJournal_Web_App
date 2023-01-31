from SUPJournal.database.database import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), nullable=False, unique=True)
    pass_ = db.Column(db.Text, nullable=False)
    e_mail = db.Column(db.Text, nullable=False, unique=True)


