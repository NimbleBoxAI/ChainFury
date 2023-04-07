from database import db_session, User

def add_default_user():
    new_user = User("admin", "admin", "")
    db = db_session()
    db.session.add(new_user)
    db.session.commit()

