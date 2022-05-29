from os import stat_result
import time
from fastapi.testclient import TestClient
from fastapi import status
from utils.password_hashing import hash_password, verify_password
from main import app
from db.main import SessionLocal
from db.models import Otp, User
from utils.jwt import sign_jwt

client = TestClient(app)


msisdn: str = "7841631859"
name: str = "Some one"
password: str = "hiBiggerPass"
new_password: str = "NewP@ssw0rD"
confirmation: str = "dummyConfirmation"
user: User = User()

db = SessionLocal()

# generate confirmation to create user
if otp := db.query(Otp).filter(Otp.msisdn == msisdn).first():
    db.delete(otp)
    db.commit()

otp = Otp(msisdn=msisdn, code="123456", confirmation=confirmation)
db.add(otp)
db.commit()


def test_create_user():
    # delete user if exists
    if existing_user := db.query(User).filter(User.msisdn == msisdn).first():
        db.delete(existing_user)
        db.commit()

    #
    endpoint = "/api/user/create"
    request_data = {
        "msisdn": msisdn,
        "name": name,
        "password": password,
        "otp_confirmation": "wrongConfirmation",
    }

    # wrong confirmation
    response = client.post(endpoint, json=request_data)
    # print(response.json())
    assert response.status_code == 409
    # print(response.json())
    assert response.json()["status"] == "failed"
    assert response.json()["error"]["code"] == 202

    # correct confirmation
    request_data["otp_confirmation"] = confirmation
    response = client.post(endpoint, json=request_data)
    # print(response.json())
    assert response.status_code == 200
    global user
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    assert response.json()["data"] == {
        "id": user.id,
        "msisdn": user.msisdn,
        "name": name,
        # "email": user.email,
        # "profile_pic_url": user.profile_pic_url,
    }

    # create user again
    response = client.post(endpoint, json=request_data)
    # print(response.json())
    assert response.status_code == 403
    assert response.json()["status"] == "failed"
    assert response.json()["error"]["code"] == 201


access_token: str = ""
refresh_token: str = ""


def test_login_user():
    # login with not found msisdn
    response = client.post(
        "/api/user/login", json={"msisdn": "10202011", "password": password}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # login with wrong credentials
    response = client.post(
        "/api/user/login", json={"msisdn": msisdn, "password": "00000000"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # login with correct credentials
    response = client.post(
        "/api/user/login", json={"msisdn": msisdn, "password": password}
    )
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # print(data)
    global access_token
    global refresh_token
    # implicit assertion of access_token and refresh_token
    access_token = data["data"]["access_token"]
    refresh_token = data["data"]["refresh_token"]
    # print(token)
    # print(response.json())


def test_validate_user():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.post(
        "/api/user/validate", headers=headers, json={"password": password}
    )
    assert response.status_code == status.HTTP_200_OK


def test_update_profile():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.patch(
        "/api/user/profile",
        headers=headers,
        json={"name": "someone else"},
    )
    assert response.status_code == status.HTTP_200_OK
    db.expire_all()
    name = db.query(User).filter(User.msisdn == msisdn).first().name
    assert name == "someone else"


def test_generate_token():
    headers = {
        "refresh-token": refresh_token,
    }
    response = client.post(
        "api/user/token",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK

    # when refresh_token not provided.
    response = client.post(
        "api/user/token",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token():
    expired_token = sign_jwt({"msisdn": msisdn}, 1)
    time.sleep(1.1)

    headers = {
        "Authorization": f"Bearer {expired_token}",
        "Content-Type": "application/json",
    }
    response = client.post(
        "/api/user/validate", headers=headers, json={"password": password}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # print(response.json())


def test_get_profile():
    headers = {"Authorization": f"Bearer {access_token}"}
    # print({"at": access_token, "rt": refresh_token})
    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    assert response.json()["data"]["id"] == user.id


def test_reset_password():
    headers = {"Content-Type": "application/json"}
    response = client.post(
        "/api/user/reset_password",
        json={
            "msisdn": msisdn,
            "password": new_password,
            "otp_confirmation": confirmation,
        },
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    db.expire_all()
    user = db.query(User).filter(User.msisdn == msisdn).first()
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:", user.password)
    assert verify_password(new_password, user.password)

    # test user not found
    response = client.post(
        "/api/user/reset_password",
        json={
            "msisdn": "10452201111",
            "password": password,
            "otp_confirmation": confirmation,
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # test wrong otp confirmation
    response = client.post(
        "/api/user/reset_password",
        json={
            "msisdn": msisdn,
            "password": new_password,
            "otp_confirmation": "wrongconfirmation",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    response = client.post(
        "/api/user/reset_password",
        json={"msisdn": msisdn, "password": password, "otp_confirmation": confirmation},
        headers=headers,
    )


def test_wallet():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f"/api/number/wallet?msisdn={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


def test_subscriptions():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f"/api/number/subscriptions?msisdn={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


def test_sim_status():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/api/number/status?msisdn={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK


def test_charge_voucher():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.post(
        "/api/number/charge-voucher",
        headers=headers,
        json={"msisdn": msisdn, "pincode": 1111},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    # print(response.json())


def test_redeem_registration_gift():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.post(
        "/api/number/redeem-registration-gift", headers=headers, json={"msisdn": msisdn}
    )
    # print(response.json())
    assert response.status_code == status.HTTP_200_OK


code: str


def test_request_otp():
    global code
    headers = {"Content-Type": "application/json"}
    response = client.post("/api/otp/request", headers=headers, json={"msisdn": msisdn})
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    otp = db.query(Otp).filter(Otp.msisdn == msisdn).first()
    assert otp
    code = otp.code


def test_confirm_otp():
    global confirmation
    global code
    # Invalid msisdn
    response = client.post(
        "/api/otp/confirm", json={"msisdn": "00000000", "code": code}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = client.post("/api/otp/confirm", json={"msisdn": msisdn, "code": code})
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    confirmation = response.json()["data"]["confirmation"]


def test_verify_otp():
    # invalid msisdn
    response = client.post(
        "/api/otp/verify", json={"msisdn": "00000000", "confirmation": confirmation}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # invalid confirmation
    response = client.post(
        "/api/otp/verify", json={"msisdn": msisdn, "confirmation": "I22Q564JqsdSD"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = client.post(
        "/api/otp/verify", json={"msisdn": msisdn, "confirmation": confirmation}
    )
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


def test_logout():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/user/logout", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()
    db.expire_all()
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user.refresh_token is None


def test_delete():
    test_login_user()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/user/delete", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert not db.query(User).filter(User.msisdn == msisdn).first()
    # print(response.json())


if __name__ == "__main__":
    test_create_user()
    test_login_user()
    test_validate_user()
    test_expired_token()
    test_get_profile()
    test_reset_password()
    test_sim_status()
    test_wallet()
    test_subscriptions()
    test_request_otp()
    time.sleep(2)
    test_confirm_otp()
    test_verify_otp()
    test_redeem_registration_gift()
    test_delete()
