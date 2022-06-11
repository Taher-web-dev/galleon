from db.main import SessionLocal
from db.models import Otp
from .utils import gen_alphanumeric


def create_otp(msisdn: str, code: str, confirmation: str | None = None) -> Otp:
    with SessionLocal() as session:
        otp = Otp(msisdn=msisdn, code=code)
        if confirmation:
            otp.confirmation = confirmation
        session.add(otp)
        session.commit()
        session.refresh(otp)


def get_otp(msisdn: str) -> Otp | None:
    with SessionLocal() as session:
        return session.query(Otp).filter(Otp.msisdn == msisdn).first()


def delete_otp(msisdn: str) -> None:
    with SessionLocal() as session:
        if otp := get_otp(msisdn):
            session.delete(otp)
            session.commit()


def increment_otp_tries(otp: Otp) -> None:
    with SessionLocal() as session:
        otp.tries += 1
        session.add(otp)
        session.commit()
        session.refresh(otp)


def gen_otp_confirmation(otp: Otp) -> None:
    with SessionLocal() as session:
        otp.confirmation = gen_alphanumeric()
        session.add(otp)
        session.commit()
        session.refresh(otp)
