from fastapi.testclient import TestClient
import json
from main import app

client = TestClient(app)

def test_debug_sample():
    response = client.get("/debug/sample")
    assert response.status_code == 200
    assert response.json() == {'users': ['a', 'b', 'c']}


def test_register_user():
    response = client.post("/user/register", json={"name":"Ali baba", "msisdn":"905070704747", "password":"Hello", "otp_confirmation":"123"})
    assert response.status_code == 200

access_token : str = ""
refresh_token : str = ""

def test_refresh_user():
    response = client.post("/user/auth/refresh", json={"msisdn": "905070704747", "password": "hello"})
    data = response.json()
    global access_token
    global refresh_token
    if "access_token" in data and "refresh_token" in data:
        access_token = data["access_token"]["token"]
        refresh_token = data["refresh_token"]["token"]
    # print(json.dumps(token))
    assert response.status_code == 200

def test_get_profile():
    headers = {"Authorization": "Bearer " + access_token}
    # print(json.dumps({"at": access_token, "rt": refresh_token}))
    response = client.get("/user/profile", headers = headers)
    print(json.dumps(response.json()))



if __name__ == "__main__":
    test_refresh_user()
    test_get_profile()

