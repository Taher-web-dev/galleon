""" OTP api set """

from fastapi import APIRouter
from pydantic import BaseModel
from .utils import gen_alphanumeric, gen_numeric, slack_notify
from utils.db import Otp, db

# from typing import Optional

router = APIRouter()

@router.post('/request')
async def generate(msisdn: str):
    """ Request new Otp """

    # If a prior otp exists, delete it.
    otp = db.query(Otp).filter(Otp.msisdn==msisdn).first()
    if otp:
        db.delete(otp)
        db.commit()
    
    code = gen_numeric()
    otp = Otp(msisdn=msisdn, code=code)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    slack_notify(msisdn, code)
    return {"msisdn": otp.msisdn}

class OtpConfirm(BaseModel):
    msisdn: str # Optional[str]
    code: str

@router.post('/confirm')
async def confirm(confirm: OtpConfirm):
    """ Confirm Otp """
    otp = db.query(Otp).filter(Otp.msisdn==confirm.msisdn).first()
    if otp: 
        otp.tries += 1
        db.commit()
        db.refresh(otp)
        if otp.code == confirm.code:
            otp.confirmation = gen_alphanumeric()
            db.commit()
            db.refresh(otp)
            return {"status": "success", "msisdn": confirm.msisdn, "confirmation": otp.confirmation}
    return {"status": "failed"}


def verify(msisdn: str, confirmation: str):
    otp = db.query(Otp).filter(Otp.msisdn==msisdn).first()
    return otp and otp.confirmation and otp.confirmation == confirmation
    

class OtpVerify(BaseModel):
    msisdn: str # Optional[str]
    confirmation: str

@router.post('/verify')
async def api_verify(otp_verify: OtpVerify):
    """Verify otp status"""
    if verify(otp_verify.msisdn, otp_verify.confirmation): 
        return {"msisdn": otp_verify.msisdn, "status": "success"}
    return {"status": "failed"}
