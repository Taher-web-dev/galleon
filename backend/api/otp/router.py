""" OTP api set """

from fastapi import APIRouter, Body
from .utils import gen_alphanumeric, gen_numeric, slack_notify
from ..number.zend import zend_send_sms
from utils.db import Otp, db
from utils.error import Error
from typing import Any

router = APIRouter()

@router.post('/request', response_model=dict[str, Any])
async def send_otp(msisdn: str = Body(..., embed=True)) -> dict[str,Any]: 
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
    response = zend_send_sms(msisdn, f"Your otp code is {code}")
    slack_notify(msisdn, code)
    return response


@router.post('/confirm', response_model=dict[str,Any])
async def confirm(msisdn: str = Body(...), code: str = Body(...)) -> dict[str, Any]:
    """ Confirm Otp """
    otp = db.query(Otp).filter(Otp.msisdn==msisdn).first()
    if otp: 
        otp.tries += 1
        db.commit()
        db.refresh(otp)
        if otp.code == code:
            otp.confirmation = gen_alphanumeric()
            db.commit()
            db.refresh(otp)
            return {"status": "success", "confirmation": otp.confirmation}
    return Error().dict()


@router.post('/verify', response_model=dict[str,Any])
async def api_verify(msisdn: str = Body(...), confirmation: str = Body(...)) -> dict[str,Any]:
    """Verify otp status (internal use)"""
    otp = db.query(Otp).filter(Otp.msisdn==msisdn).first()
    if otp and otp.confirmation and otp.confirmation == confirmation:
        return {"status": "success"}
    return Error().dict()
