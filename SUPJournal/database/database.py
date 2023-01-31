from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
URI = f"postgresql://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@localhost/SUPJournal"
