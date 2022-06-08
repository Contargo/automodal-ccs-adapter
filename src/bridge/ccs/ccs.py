import time
from threading import Thread
from typing import Any

import requests
from flask import Flask, request

from bridge.ccs.enums import CCSFeatureType
from bridge.ccs.helper import generate_metadata, generate_feature
from bridge.ccs.job import CCSJobState
from bridge.sps.client import SpsClient
from bridge.sps.types import spsbyte

app = Flask(__name__)


class CCS:
    locaton: str = "terminal"
    type: str = "crane"
    name: str = "PSKran"

    def __init__(self, sps_client: SpsClient, tams_url: str = "http://localhost:9998"):
        self.sps_client = sps_client
        self.tams_url = tams_url
        self.app = Flask(
            "ccs",
        )
        self.state = CCSJobState()
        self.add_endpoints()
        self.worker_rest: Thread = Thread(
            target=self.rest,
            args=(),
            name="CCS Worker",
            daemon=True,
        )

        self.worker_sps: Thread = Thread(
            target=self.sps,
            args=(),
            name="CCS Worker",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_rest.start()

    def add_endpoints(self) -> None:
        self.app.add_url_rule("/job", "job", self.job, methods=["POST"])
        self.app.add_url_rule("/details", "details", self.details, methods=["GET"])

    def rest(self) -> None:
        self.app.run(host="127.0.0.1", port=9999)

    def sps(self) -> None:
        status = self.sps_client.read_value("job_status", spsbyte)
        if status == 0x01:
            self.state.job_done()
            # delete old job (and send done status to tams)
        time.sleep(0.1)


    def job(self, *args, **kwargs) -> Any: # type: ignore
        print(f"{args=}")
        print(f"{kwargs=}")

        ret = self.state.set_new_job(str(request.json))

        if ret == "invalid":
            return "Invalid input", 405
        if ret == "has job":
            return self.state.get_job_as_json(), 409
        if ret == "OK":
            return "OK", 200
        return "unknown error", 500

    def send_status(self) -> None:
        ret = requests.post(
            f"{self.tams_url}/state", json=self.state.get_state_as_json()
        )
        if ret == "OK":
            print("juhu")

    def send_alarm(self) -> None:
        pass

    def send_metric(self) -> None:
        pass

    @staticmethod
    def details() -> Any:
        return {
            "event": generate_metadata("details"),
            "feature": [generate_feature(CCSFeatureType.FINAL_LANDING)],
        }, 200

    def shutdown(self) -> None:
        pass
