from app import db, User

db.create_all()

u = User(email="0", password="0")
db.session.add(u)
db.session.commit()
