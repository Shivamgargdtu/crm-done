import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import bcrypt

MONGO_URL = os.environ.get("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URL)
db = client["wedus_crm"]

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

async def create_user():
    user = {
        "email": "shivamgarg612sg@gmail.com",
        "password_hash": hash_password("12345678"),
        "name": "Shivam",
        "role": "admin"
    }

    await db.users.insert_one(user)
    print("User created ✅")

asyncio.run(create_user())