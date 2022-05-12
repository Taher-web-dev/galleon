from fastapi.testclient import TestClient
from fastapi import status
import json
from main import app
from utils.db import db, Otp

client = TestClient(app)


msisdn: str = "7841631859"
name: str = "Some one"
password: str = "hi"
confirmation: str = "123"

def test_create_user():
    response = client.post("/api/user/create",
                           json={
                               "name":name, 
                               "msisdn":msisdn, 
                               "password":password, 
                               "otp_confirmation":confirmation})
    print(json.dumps(response.json()))
    assert response.status_code == 200

access_token : str = ""
refresh_token : str = ""

def test_login_user():
    response = client.post("/api/user/login", json={"msisdn": msisdn, "password": password})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    global access_token
    global refresh_token
    if "access_token" in data and "refresh_token" in data:
        access_token = data["access_token"]["token"]
        refresh_token = data["refresh_token"]["token"]
        return
    assert "Missing tokens"
    # print(json.dumps(token))
    # print(json.dumps(response.json()))

def test_get_profile():
    headers = {"Authorization": "Bearer " + access_token}
    # print(json.dumps({"at": access_token, "rt": refresh_token}))
    response = client.get("/api/user/profile", headers = headers)
    assert response.status_code == status.HTTP_200_OK
    # print(json.dumps(response.json()))

def test_update_profile():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.patch("/api/user/profile", json={"password":"...."}, headers = headers)
    assert response.status_code == status.HTTP_200_OK
    # print(json.dumps(response.json()))

def test_redeem_registration_gift():
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }
    response = client.post("/api/msisdn/redeem-registration-gift", headers = headers, json={"msisdn": msisdn})
    print(json.dumps(response.json()))
    assert response.status_code == status.HTTP_200_OK


def test_logout():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.post("/api/user/logout", headers = headers)
    assert response.status_code == status.HTTP_200_OK
    assert {"status":"success"} == response.json()

def test_delete():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.post("/api/user/delete", headers = headers)
    assert response.status_code == status.HTTP_200_OK
    # print(json.dumps(response.json()))

def test_wallet():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.get(f"/api/msisdn/wallet/{msisdn}", headers = headers)
    assert response.status_code == status.HTTP_200_OK
    # print(json.dumps(response.json()))

def test_subscriptions():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.get(f"/api/msisdn/subscriptions/{msisdn}", headers = headers)
    assert response.status_code == status.HTTP_200_OK
    #print(json.dumps(response.json()))

def test_charge_voucher():
    headers = {
        "Authorization": "Bearer " + access_token, 
        "Content-Type": "application/json"
    }
    response = client.post("/api/msisdn/charge-voucher", headers = headers, json={'msisdn': msisdn, 'pincode': 1111})
    assert response.status_code == status.HTTP_200_OK, response.json()
    # print(json.dumps(response.json()))

def test_sim_status():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.get(f"/api/msisdn/status/{msisdn}", headers = headers)
    assert response.status_code == status.HTTP_200_OK

code: str
def test_request_otp():
    global code
    headers={"Content-Type": "application/json"}
    response = client.post("/api/otp/request", headers=headers, json={'msisdn': msisdn})
    assert response.status_code == status.HTTP_200_OK
    print(json.dumps(response.json()))
    otp = db.query(Otp).filter(Otp.msisdn==msisdn).first()
    assert otp 
    code = otp.code

def test_confirm_otp(): 
    global confirmation
    global code
    response = client.post("/api/otp/confirm", json={'msisdn': msisdn, 'code': code})
    assert response.status_code == status.HTTP_200_OK
    #print(json.dumps(response.json()))
    confirmation = response.json()['confirmation']

def test_verify_otp():
    response = client.post("/api/otp/verify", json={'msisdn': msisdn, 'confirmation': confirmation})
    assert response.status_code == status.HTTP_200_OK
    #print(json.dumps(response.json()))

if __name__ == "__main__":
    test_create_user()
    test_login_user()
    #test_get_profile()
    #test_update_profile()
    #test_sim_status()
    #test_wallet()
    #test_subscriptions()
    #test_request_otp() 
    #sleep(2)
    #test_confirm_otp() 
    #test_verify_otp() 
    test_redeem_registration_gift()
    test_delete()
    pass

