""" Try out """

from db import User, db

users = db.query(User).all()

for user in users:
    print(user.id, user.name, user.email)
