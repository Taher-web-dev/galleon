from fastapi.testclient import TestClient
import json
from main import app

client = TestClient(app)

def test_debug_sample():
    response = client.get("/debug/sample")
    assert response.status_code == 200
    assert response.json() == {'users': ['a', 'b', 'c']}


msisdn: str = "96478"
name: str = "Some one"
password: str = "hi"
otp_confirmation: str = "123"

def test_register_user():
    response = client.post("/user/register", json={"name":name, "msisdn":msisdn, "password":password, "otp_confirmation":otp_confirmation})
    print(json.dumps(response.json()))
    assert response.status_code == 200

access_token : str = ""
refresh_token : str = ""

def test_refresh_user():
    response = client.post("/user/auth/refresh", json={"msisdn": msisdn, "password": password})
    data = response.json()
    global access_token
    global refresh_token
    if "access_token" in data and "refresh_token" in data:
        access_token = data["access_token"]["token"]
        refresh_token = data["refresh_token"]["token"]
    # print(json.dumps(token))
    print(json.dumps(response.json()))
    assert response.status_code == 200

def test_get_profile():
    headers = {"Authorization": "Bearer " + access_token}
    # print(json.dumps({"at": access_token, "rt": refresh_token}))
    response = client.get("/user/profile", headers = headers)
    print(json.dumps(response.json()))

def test_update_profile():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.post("/user/profile", json={"password":"...."}, headers = headers)
    print(json.dumps(response.json()))


def test_delete():
    headers = {"Authorization": "Bearer " + access_token}
    response = client.post("/user/delete", headers = headers)
    print(json.dumps(response.json()))



if __name__ == "__main__":
    test_register_user()
    test_refresh_user()
    test_get_profile()
    test_update_profile()
    test_delete()

