from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()

user = User(
    email="shivamgarg612sg@gmail.com",
    hashed_password=get_password_hash("12345678"),
    name="Shivam",
    role="admin"
)

db.add(user)
db.commit()
db.close()

print("User created successfully!")