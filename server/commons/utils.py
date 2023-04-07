from sqlalchemy.exc import IntegrityError
from database import db_session, User

def add_default_user():
    new_user = User(username="admin", password="admin", meta="")
    db = db_session()
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        print("Not adding default user")
