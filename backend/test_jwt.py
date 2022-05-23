from utils.jwt import sign_jwt, decode_jwt


def test_jwt():
    data = {"msisdn": "12341234"}
    token = sign_jwt(data)
    clear = decode_jwt(token)
    assert clear == data


if __name__ == "__main__":
    test_jwt()
