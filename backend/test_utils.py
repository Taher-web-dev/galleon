from fastapi import status


def check_validation(response):
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "failed" == response.json().get("status")
    assert "validation" == response.json().get("error").get("type")


def check_valid_access_token(response):
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "failed" == response.json().get("status")
    assert "token" == response.json().get("error").get("type")


def check_invalid_msisdn(response):
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "failed" == response.json().get("status")
    assert "number" == response.json().get("error").get("type")
