import time
from locust import HttpUser, task, between


class Number(HttpUser):
    wait_time = between(0.5, 5)

    @task
    def status(self):
        """/api/number/status"""
        self.client.get("/api/number/status?msisdn=7839921514")


# class Otp(HttpUser):
#     pass


# class User(HttpUser):
#     pass

# def on_start(self):
#     self.client.post("/login", json={"username": "foo", "password": "bar"})
