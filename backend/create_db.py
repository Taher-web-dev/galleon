""" Create database example """

from utils.db import User, Otp, engine, Base, db

Base.metadata.create_all(bind=engine)

msisdn = "905070704747"
# user = User(name="Ali baba", email="Hello6", msisdn=msisdn, password="World")
# db.add(user)

# otp = Otp(msisdn=msisdn, code="1234")
# db.add(otp)

# db.commit()
# db.refresh(user)

otp = db.query(Otp).filter(Otp.msisdn == msisdn).first()
otp.tries += 1
db.commit()
db.refresh(otp)
# otp = Otp.query.get(msisdn)
# user = User.query.get(msisdn=msisdn)
user = db.query(User).filter(User.msisdn == msisdn).first()

print(user.id, user.name, user.email, user.created_at, user.updated_at)
print(otp.msisdn, otp.code, otp.tries, otp.created_at, otp.updated_at)
