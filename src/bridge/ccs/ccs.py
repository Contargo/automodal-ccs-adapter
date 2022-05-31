from threading import Thread
from typing import Any

import requests
from flask import Flask, request

from ccs.enums import CCSFeatureType
from ccs.helper import generate_metadata, generate_feature
from ccs.job import CCSJobState

app = Flask(__name__)


class CCS:
    locaton: str = "terminal"
    type: str = "crane"
    name: str = "PSKran"

    def __init__(self, tams_url: str = "http://localhost:9998"):
        self.tams_url = tams_url
        self.app = Flask(
            "ccs",
        )
        self.state = CCSJobState()
        self.add_endpoints()
        self.worker_rest: Thread = Thread(
            target=self.start,
            args=(),
            name="CCS Worker",
            daemon=True,
        )
        self.worker_rest.start()

    def add_endpoints(self) -> None:
        self.app.add_url_rule("/job", "job", self.job, methods=["POST"])
        self.app.add_url_rule("/details", "details", self.details, methods=["GET"])

    def start(self) -> None:
        self.app.run(host="127.0.0.1", port=9999)

    def job(self, *args, **kwargs) -> Any:
        print(f"{args=}")
        print(f"{kwargs=}")

        ret = self.state.set_new_job(request.json)

        if ret == "invalid":
            return "Invalid input", 405
        if ret == "has job":
            return self.state.get_job_as_json(), 409
        if ret == "OK":
            return "OK", 200
        return "unknown error", 500

    def send_status(self):
        ret = requests.post(f"{self.tams_url}/state", json=self.state.get_state_as_json())
        if ret == "OK":
            print("juhu")
            
    def send_alarm(self):
        pass
    
    def send_metric(self):
        pass

    @staticmethod
    def details() -> Any:
        return {
            "event": generate_metadata("details"),
            "feature": [generate_feature(CCSFeatureType.FINAL_LANDING)],
        }, 200

    def shutdown(self):
        pass
