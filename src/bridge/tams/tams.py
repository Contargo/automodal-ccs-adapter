import time
from random import random
from threading import Thread, Event
from typing import Any

import requests
from flask import Flask, request
from requests import ConnectionError

from bridge.tams.enums import CCSFeatureType
from bridge.tams.helper import generate_metadata, generate_feature, dataclass_to_json
from bridge.tams.job import CCSJobState
from bridge.sps.client import SpsClient
from bridge.sps.types import spsbyte
from bridge.tams.types import CCSCraneDetails, CCSEvent, CCSFeature


class CCS:
    locaton: str = "terminal"
    type: str = "crane"
    name: str = "PSKran"

    def __init__(self, sps_client: SpsClient, tams_url: str = "http://localhost:9998"):
        self.sps_client = sps_client
        self.tams_url = tams_url
        self.shutdown_event = Event()
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
        
        self.worker_ccs: Thread = Thread(
            target=self.ccs,
            args=(),
            name="CCS Worker",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_rest.start()
        self.worker_sps.start()
        self.worker_ccs.start()

    def add_endpoints(self) -> None:
        self.app.add_url_rule("/job", "job_post", self.job_post, methods=["POST"])
        self.app.add_url_rule("/job", "job_get", self.job_get, methods=["GET"])
        self.app.add_url_rule("/details", "details", self.details, methods=["GET"])

    def rest(self) -> None:
        self.app.run(host="127.0.0.1", port=9999)

    def sps(self) -> None:
        while not self.shutdown_event.is_set():
            status = self.sps_client.read_value("job_status", spsbyte)
            if status == 0x01:
                self.state.job_done()
                # delete old job (and send done status to tams)
            time.sleep(0.1)

    def ccs(self):
        while not self.shutdown_event.is_set():
            self.send_status()
            time.sleep(1)
            if random() > 0.95:
                self.state.job_done()
        

    def job_post(self, *args, **kwargs) -> Any: # type: ignore
        ret = self.state.set_new_job(str(request.json))

        print(f"TAMS job: {ret}")
        if ret == "invalid":
            return "Invalid input", 405
        if ret == "has job":
            return self.state.get_job_as_json(), 409
        if ret == "OK":
            return "OK", 200
        return "unknown error", 500

    def job_get(self) -> Any:
        if self.state.has_job():
            return self.state.get_job_as_json(), 200
        else: 
            return "no job", 404

    def send_status(self) -> None:
        try:
            ret = requests.post(
                f"{self.tams_url}/state", json=self.state.get_state_as_json()
            )
            #if ret.text == "OK":
            #    print("send status successfull")
        except ConnectionError:
            return
        
    def send_alarm(self) -> None:
        try:
            ret = requests.post(
                f"{self.tams_url}/alarm", json={}
            )
            if ret == "OK":
                print("juhu")
        except ConnectionError:
            return

    def send_metric(self) -> None:
        ret = requests.post(
            f"{self.tams_url}/metric", json={}
        )
        if ret == "OK":
            print("juhu")

    @staticmethod
    def details() -> Any:
        details = CCSCraneDetails()
        details.event = CCSEvent(type=f"net.contargo.logistics.tams.details")
        details.feature = [CCSFeature(
            type=CCSFeatureType.FINAL_LANDING,
        )]
        return dataclass_to_json(details), 200

    def shutdown(self) -> None:
        self.shutdown_event.set()
