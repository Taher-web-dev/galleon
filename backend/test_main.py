import time
from fastapi.testclient import TestClient
from fastapi import status
from utils.password_hashing import verify_password
from main import app
from utils.db import db, Otp, User

client = TestClient(app)


msisdn: str = "7841631859"
name: str = "Some one"
password: str = "hiBiggerPass"
confirmation: str = "123"
user: User = None


def test_create_user():
    response = client.post(
        "/api/user/create",
        json={
            "msisdn": msisdn,
            "name": name,
            "password": password,
            "otp_confirmation": confirmation,
        },
    )
    print(response.json())
    assert response.status_code == 200
    global user
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    assert response.json() == {
        "id": user.id,
        "msisdn": user.msisdn,
        "name": name,
        "email": user.email,
        "profile_pic_url": user.profile_pic_url,
    }


access_token: str = ""
refresh_token: str = ""


def test_login_user():
    response = client.post(
        "/api/user/login", json={"msisdn": msisdn, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    global access_token
    global refresh_token
    # implicit assertion of access_token and refresh_token
    access_token = data["access_token"]["token"]
    refresh_token = data["refresh_token"]["token"]
    # print(token)
    # print(response.json())


def test_get_profile():
    headers = {"Authorization": f"Bearer {access_token}"}
    # print({"at": access_token, "rt": refresh_token})
    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    assert response.json()["id"] == user.id


def test_update_profile():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.patch(
        "/api/user/profile", json={"password": "........"}, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert verify_password("........", user.password)
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


def test_logout():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/user/logout", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert {"status": "success"} == response.json()
    assert user.refresh_token is None


def test_delete():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/user/delete", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert not db.query(User).filter(User.msisdn == msisdn).first()
    # print(response.json())


def test_wallet():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(
        "/api/number/wallet", json={"msisdn": msisdn}, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


def test_subscriptions():
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(
        "/api/number/subscriptions", json={"msisdn": msisdn}, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


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


def test_sim_status():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(
        "/api/number/status", headers=headers, json={"msisdn": msisdn}
    )
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
    response = client.post("/api/otp/confirm", json={"msisdn": msisdn, "code": code})
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    confirmation = response.json()["confirmation"]


def test_verify_otp():
    response = client.post(
        "/api/otp/verify", json={"msisdn": msisdn, "confirmation": confirmation}
    )
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


if __name__ == "__main__":
    test_create_user()
    test_login_user()
    test_get_profile()
    test_update_profile()
    test_sim_status()
    test_wallet()
    test_subscriptions()
    test_request_otp()
    time.sleep(2)
    test_confirm_otp()
    test_verify_otp()
    test_redeem_registration_gift()
    test_delete()
