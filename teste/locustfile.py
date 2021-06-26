import random

from locust import HttpUser, task

ids = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110]


class LoadTesting(HttpUser):
    @task
    def hello_world(self):
        id = random.choice(ids)
        self.client.get("/items/" + str(id) + "?q=ps%20-aux%20", name="/id/[id]")
