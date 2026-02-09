from locust import HttpUser, task, between
import os


class InferenceUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def infer(self):
        url = os.getenv("API_PATH", "/v1/infer")
        self.client.post(url, json={"model": "gpt2", "prompt": "hello world"})





