from app import db, User
from werkzeug.security import generate_password_hash

db.create_all()

u = User(email="0", password=generate_password_hash("0"))
db.session.add(u)
db.session.commit()
