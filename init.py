from app import db, User, Homework
from werkzeug.security import generate_password_hash

db.create_all()

u = User(email="0", password=generate_password_hash("0"))
db.session.add(u)
db.session.commit()

for i in range(2):
    hw = Homework(status="CLOSED", reference=f"data/ref{i + 1}.csv")
    db.session.add(hw)

hw = Homework(status="OPEN", reference="data/ref3.csv")
db.session.add(hw)
db.session.commit()
