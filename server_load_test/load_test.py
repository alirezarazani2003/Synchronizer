from locust import HttpUser, task, between
import json

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

request_payload = load_json('request.json')


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_sync_subs(self):
        self.client.post("http://localhost:5223/get_sync_subs", json=request_payload)
