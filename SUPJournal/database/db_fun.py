from SUPJournal.database.models import Workout, User
from SUPJournal.tools.gpx import GpxFile
from SUPJournal.database.database import db

def add_training_to_bd(gpx_file, user_id):
    training = GpxFile(gpx_file)
    workout = Workout(owner_id=user_id,
                      date=training.training_date,
                      dist=training.dist,
                      tr_time=training.time,
                      gpx=gpx_file)
    db.session.add(workout)
    db.session.commit()