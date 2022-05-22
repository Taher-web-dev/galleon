from fastapi.testclient import TestClient
from fastapi import status
from utils.password_hashing import verify_password
from main import app
from utils.db import db, Otp, User

client = TestClient(app)


msisdn: str = "7841631859"
name: str = "Some one"
password: str = "hiBiggerPass"
confirmation: str = "dummyConfirmation"
user: User = User()


# generate confirmation to create user
if otp := db.query(Otp).filter(Otp.msisdn == msisdn).first():
    db.delete(otp)
    db.commit()

otp = Otp(msisdn=msisdn, code="123", confirmation=confirmation)
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
    print(response.json())
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
    print(response.json())
    assert response.status_code == 403
    assert response.json()["status"] == "failed"
    assert response.json()["error"]["code"] == 201


access_token: str = ""
refresh_token: str = ""


def test_login_user():
    response = client.post(
        "/api/user/login", json={"msisdn": msisdn, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    print(data)
    global access_token
    global refresh_token
    # implicit assertion of access_token and refresh_token
    access_token = data["data"]["access_token"]
    refresh_token = data["data"]["refresh_token"]
    # print(token)
    # print(response.json())


def test_get_profile():
    headers = {"Authorization": f"Bearer {access_token}"}
    # print({"at": access_token, "rt": refresh_token})
    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    assert response.json()["data"]["id"] == user.id
    # assert response.json()["id"] == user.id


def test_update_profile():
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.patch(
        "/api/user/profile", json={"password": "........"}, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert verify_password("........", user.password)
    # print(response.json())


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
    response = client.post("/api/otp/confirm", json={"msisdn": msisdn, "code": code})
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())
    confirmation = response.json()["data"]["confirmation"]


def test_verify_otp():
    response = client.post(
        "/api/otp/verify", json={"msisdn": msisdn, "confirmation": confirmation}
    )
    assert response.status_code == status.HTTP_200_OK
    # print(response.json())


if __name__ == "__main__":
    test_create_user()
    """
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
    """
