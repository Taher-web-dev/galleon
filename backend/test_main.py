import json
import time
from fastapi.testclient import TestClient
from fastapi import status
from test_utils import check_invalid_msisdn, check_validation, check_valid_access_token
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
confirmation: str = "fjuGQYmZvCBsQbEZ"
user: User = User()

db = SessionLocal()

# cleaning otp
if otp := db.query(Otp).filter(Otp.msisdn == msisdn).first():
    db.delete(otp)
if otp := db.query(Otp).filter(Otp.msisdn == "7555555555").first():
    db.delete(otp)
    db.commit()

# cleaning usese
if user := db.query(User).filter(User.msisdn == msisdn).first():
    db.delete(user)
if user := db.query(User).filter(User.msisdn == "7555555555").first():
    db.delete(user)
    db.commit()

# generate confirmation to create user
otp = Otp(msisdn=msisdn, code="123456", confirmation=confirmation)
db.add(otp)
db.commit()


code: str = "123456"
access_token: str = ""
refresh_token: str = ""


def test_request_otp():
    global code
    headers = {"Content-Type": "application/json"}
    endpoint = "/api/otp/request"

    # Invalid msisdn format
    response = client.post(endpoint, headers=headers, json={"msisdn": "7841631859b"})
    check_validation(response)

    response = client.post(endpoint, headers=headers, json={"msisdn": msisdn})
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()

    otp = db.query(Otp).filter(Otp.msisdn == msisdn).first()
    assert otp
    code = otp.code


def test_confirm_otp():
    global confirmation
    global code
    endpoint = "/api/otp/confirm"

    # Invalid msisdn
    response = client.post(endpoint, json={"msisdn": "7800000000", "code": code})
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Invalid msisdn format
    response = client.post(endpoint, json={"msisdn": "7841631859b", "code": code})
    check_validation(response)

    # Invalid code
    response = client.post(endpoint, json={"msisdn": msisdn, "code": "000000"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" == response.json().get("status")
    assert "otp" == response.json().get("error").get("type")

    response = client.post(endpoint, json={"msisdn": msisdn, "code": code})
    assert response.status_code == status.HTTP_200_OK
    confirmation = response.json()["data"]["confirmation"]


def test_verify_otp():
    endpoint = "/api/otp/verify"

    # invalid msisdn
    response = client.post(
        endpoint, json={"msisdn": "7800000000", "confirmation": confirmation}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Invalid msisdn format
    response = client.post(
        endpoint, json={"msisdn": "7841631859b", "confirmation": confirmation}
    )
    check_validation(response)

    # invalid confirmation
    response = client.post(
        endpoint, json={"msisdn": msisdn, "confirmation": "fjuGQYmZvCBsQbEX"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.post(
        endpoint, json={"msisdn": msisdn, "confirmation": confirmation}
    )
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()


def test_create_user():
    # delete user if exists
    if existing_user := db.query(User).filter(User.msisdn == msisdn).first():
        db.delete(existing_user)
        db.commit()

    endpoint = "/api/user/create"
    request_data = {
        "msisdn": msisdn,
        "name": name,
        "password": password,
        "otp_confirmation": "fjuGQYmZvCBsQbEX",
    }

    # Invalid msisdn format
    response = client.post(endpoint, json={**request_data, "msisdn": "7841631859b"})
    check_validation(response)

    # wrong confirmation
    response = client.post(endpoint, json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["status"] == "failed"
    assert response.json()["error"]["code"] == 202

    # correct confirmation
    request_data["otp_confirmation"] = confirmation
    response = client.post(
        endpoint,
        json={
            **request_data,
            "msisdn": msisdn,
            "name": name,
        },
    )

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

    assert response.status_code == 403
    assert response.json()["status"] == "failed"
    assert response.json()["error"]["code"] == 201


def test_login_user():
    endpoint = "/api/user/login"

    # login with not found msisdn
    response = client.post(
        endpoint, json={"msisdn": "7810202011", "password": password}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # login with wrong credentials
    response = client.post(endpoint, json={"msisdn": msisdn, "password": "00000000"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # login with correct credentials
    response = client.post(endpoint, json={"msisdn": msisdn, "password": password})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    global access_token
    global refresh_token

    # implicit assertion of access_token and refresh_token
    access_token = data["data"]["access_token"]
    refresh_token = data["data"]["refresh_token"]


def test_validate_user():
    endpoint = "/api/user/validate"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # wrong password
    response = client.post(endpoint, headers=headers, json={"password": "passwordx"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "failed" == response.json().get("status")
    assert "auth" == response.json().get("error").get("type")

    response = client.post(endpoint, headers=headers, json={"password": password})
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post(endpoint, headers=headers, json={"password": password})
    check_valid_access_token(response)


def test_update_profile():
    endpoint = "/api/user/profile"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.patch(endpoint, headers=headers, json={"name": "someone else"})
    assert response.status_code == status.HTTP_200_OK
    db.expire_all()
    name = db.query(User).filter(User.msisdn == msisdn).first().name
    assert name == "someone else"

    response = client.patch(endpoint, headers=headers, json={"name": "someone else"})
    assert response.status_code == status.HTTP_200_OK

    msisdn_new = "7555555555"
    # request opt
    client.post("/api/otp/request", headers=headers, json={"msisdn": msisdn_new})
    # request new confirmation
    response = client.post(
        "/api/otp/confirm", json={"msisdn": msisdn_new, "code": code}
    )
    confirmation_new = response.json()["data"]["confirmation"]
    # create new user
    response = client.post(
        "/api/user/create",
        json={
            "password": "password",
            "otp_confirmation": confirmation_new,
            "msisdn": msisdn_new,
            "name": "tenno",
        },
    )
    # fail on change name to exsisting one
    response = client.patch(endpoint, headers=headers, json={"name": "tenno"})
    #! TODO investigate why 500 is being returned
    #! instead of 409 as set in SQLAE
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.patch(endpoint, headers=headers, json={"name": "tenno"})
    check_valid_access_token(response)


def test_generate_token():
    endpoint = "api/user/token"
    headers = {
        "refresh-token": refresh_token,
    }
    response = client.post(endpoint, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # when refresh_token not valid.
    headers = {
        "refresh-token": "invalid_refresh_token",
    }
    response = client.post(endpoint, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["code"] == 101
    assert response.json()["error"]["message"] == "The Refresh-Token is not valid"

    # using access token
    response = client.post(
        endpoint,
        headers={
            "refresh-token": access_token,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_and_invalid_token():
    expired_token = sign_jwt({"msisdn": msisdn}, 1)
    time.sleep(1.1)

    headers = {
        "Authorization": f"Bearer {expired_token}",
        "Content-Type": "application/json",
    }
    response = client.post(
        "/api/user/validate", headers=headers, json={"password": password}
    )
    assert response.status_code == status.HTTP_410_GONE
    assert response.json()["error"]["code"] == 105
    assert (
        response.json()["error"]["message"]
        == "You need to renew the Access token using the refresh token"
    )


def test_get_profile():
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["id"] == user.id

    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get("/api/user/profile", headers=headers)
    check_valid_access_token(response)


def test_reset_password():
    headers = {"Content-Type": "application/json"}
    endpoint = "/api/user/reset_password"
    request_data = {
        "msisdn": msisdn,
        "password": new_password,
        "otp_confirmation": confirmation,
    }

    # Invalid msisdn format
    response = client.post(
        endpoint, json={**request_data, "msisdn": "7841631859b"}, headers=headers
    )
    check_validation(response)

    # Wrong msisdn
    response = client.post(
        endpoint, json={**request_data, "msisdn": "7841631850"}, headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "failed" == response.json().get("status")
    assert "auth" == response.json().get("error").get("type")

    # Wrong confirmation format
    response = client.post(
        endpoint,
        json={**request_data, "otp_confirmation": "7841631850"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "failed" == response.json().get("status")
    assert "validation" == response.json().get("error").get("type")

    response = client.post(
        endpoint,
        json=request_data,
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()

    db.expire_all()
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert verify_password(new_password, user.password)

    # test user not found
    response = client.post(
        "/api/user/reset_password",
        json={
            "msisdn": "7842201111",
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
            "otp_confirmation": "fjuGQYmZvCBsQbEX",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "failed" == response.json().get("status")
    assert "otp" == response.json().get("error").get("type")

    # revert
    client.post(
        "/api/user/reset_password",
        json={"msisdn": msisdn, "password": password, "otp_confirmation": confirmation},
        headers=headers,
    )


def test_wallet():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    endpoint = "/api/number/wallet?msisdn"

    # Invalid msisdn format
    response = client.get(f"{endpoint}=784163185b", headers=headers)
    check_validation(response)

    # Invalid msisdn
    response = client.get(f"{endpoint}=7841631850", headers=headers)
    check_invalid_msisdn(response)

    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    check_valid_access_token(response)


def test_subscriptions():
    endpoint = "/api/number/subscriptions?msisdn"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # Invalid msisdn format
    response = client.get(f"{endpoint}=784163185b", headers=headers)
    check_validation(response)

    # Invalid msisdn
    response = client.get(f"{endpoint}=7841631850", headers=headers)
    check_invalid_msisdn(response)

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    check_valid_access_token(response)


def test_sim_status():
    endpoint = "/api/number/status?msisdn"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # Invalid msisdn format
    response = client.get(f"{endpoint}=784163185b", headers=headers)
    check_validation(response)


def test_charge_voucher():
    endpoint = "/api/number/charge-voucher"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.post(
        endpoint,
        headers=headers,
        json={"msisdn": msisdn, "pincode": 1111111111111111},
    )
    assert response.status_code == status.HTTP_200_OK

    # Invalid msisdn format
    response = client.post(
        endpoint,
        headers=headers,
        json={"msisdn": "784163185b", "pincode": 1111111111111111},
    )
    check_validation(response)

    # Invalid pincode format
    response = client.post(
        endpoint,
        headers=headers,
        json={"msisdn": msisdn, "pincode": "qsdqsdqsd"},
    )
    check_validation(response)

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post(
        endpoint,
        headers=headers,
        json={"msisdn": msisdn, "pincode": 1111111111111111},
    )
    check_valid_access_token(response)


def test_nba():
    endpoint = "/api/number/nba?msisdn"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # Invalid msisdn format
    response = client.get(f"{endpoint}=784163185b", headers=headers)
    check_validation(response)

    # Invalid msisdn
    response = client.get(f"{endpoint}=7841631850", headers=headers)
    check_invalid_msisdn(response)

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.get(f"{endpoint}={msisdn}", headers=headers)
    check_valid_access_token(response)


def test_redeem_registration_gift():
    endpoint = "/api/number/redeem-registration-gift"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.post(endpoint, headers=headers, json={"msisdn": msisdn})

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("status") == "success"
    assert response.json().get("success").get("code") == 0

    # Invalid msisdn format
    response = client.post(endpoint, headers=headers, json={"msisdn": "784163185b"})
    check_validation(response)

    # Invalid msisdn
    response = client.post(endpoint, headers=headers, json={"msisdn": "7841631850"})
    check_invalid_msisdn(response)

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post(endpoint, headers=headers, json={"msisdn": msisdn})
    check_valid_access_token(response)


def test_logout():
    endpoint = "/api/user/logout"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.delete(endpoint, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()

    db.expire_all()

    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user.refresh_token is None

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.delete(endpoint, headers=headers)
    check_valid_access_token(response)


def test_delete():
    test_login_user()
    endpoint = "/api/user/delete"

    # wrong access token
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.delete(endpoint, headers=headers)
    check_valid_access_token(response)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete(endpoint, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()
    assert not db.query(User).filter(User.msisdn == msisdn).first()


if __name__ == "__main__":
    test_create_user()
    test_login_user()
    test_validate_user()
    test_expired_and_invalid_token()
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
