import time
from random import random
from threading import Thread, Event
from typing import Any

import requests
from flask import Flask, request
from requests import ConnectionError

from bridge.sps.data import db_items
from bridge.sps.enums import SPSStatus
from bridge.tams.enums import CCSFeatureType, CCSJobType
from bridge.tams.helper import generate_metadata, generate_feature, dataclass_to_json
from bridge.tams.job import CCSJobState
from bridge.sps.client import SpsClient
from bridge.sps.types import spsbyte, spsbool, spsint, spsdint
from bridge.tams.types import CCSCraneDetails, CCSEvent, CCSFeature, CCSMetric, CCSMetricEntry


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
        state = "wait_for_job"
        while not self.shutdown_event.is_set():
            if state == "wait_for_job":
                if self.state.sps_status() in [SPSStatus.INIT, SPSStatus.WAIT]:
                    if self.state.has_job():
                        print("send new job to SPS")
                        self.state.set_sps_status(SPSStatus.RUNNING)
                        job = self.state.get_job()
                        if job.type == CCSJobType.PICK:
                            self.sps_client.write_item("JobType", spsbyte(b"\x01"))
                        if job.type == CCSJobType.DROP:
                            self.sps_client.write_item("JobType", spsbyte(b"\x02"))
                        self.sps_client.write_item("JobCoordinatesX", spsdint(job.target.x))
                        self.sps_client.write_item("JobCoordinatesY", spsdint(job.target.y))
                        self.sps_client.write_item("JobCoordinatesZ", spsdint(job.target.z))
                        self.sps_client.write_item("JobSpreaderSize", spsint(20))
                        self.sps_client.write_item("JobNewJob", spsint(1))
                        state = "wait_for_sps_in_progress"
            if state == "wait_for_sps_in_progress":
                if self.sps_client.read_value("JobStatusInProgress", spsbool):
                    state = "wait_for_done"
            if state == "wait_for_done":
                if (
                    self.state.sps_status() == SPSStatus.RUNNING
                    and self.sps_client.read_value("JobStatusDone", spsbool)
                ):
                    print(
                        f"{self.state.sps_status() == SPSStatus.RUNNING} and {self.sps_client.read_value('JobStatusDone', spsbool)}"
                    )
                    self.state.job_done()
                    print("wait for new job from tams")
                    state = "wait_for_job"
                    # delete old job (and send done status to tams)
            time.sleep(0.1)

    def ccs(self):
        while not self.shutdown_event.is_set():
            self.send_status()
            self.send_metric()
            time.sleep(1)

    def job_post(self, *args, **kwargs) -> Any:  # type: ignore
        ret = self.state.set_new_job(request.data.decode('utf-8'))

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
            # if ret.text == "OK":
            #    print("send status successfull")
        except (ConnectionError, ConnectionRefusedError):
            return

    def send_alarm(self) -> None:
        try:
            ret = requests.post(f"{self.tams_url}/alarm", json={})
            if ret == "OK":
                print("juhu")
        except ConnectionError:
            return

    def send_metric(self) -> None:
        try:
            metrics = CCSMetric()
            metrics.event = CCSEvent(type=f"net.contargo.logistics.tams.metric")
            for item in db_items:
                value = self.sps_client.read_value(item.name, item.type)
                metrics.metrics.append(
                    CCSMetricEntry(name=item.name, datatype=item.type.__name__, value=value)
                )
            ret = requests.post(f"{self.tams_url}/metric", json=dataclass_to_json(metrics))
            if ret == "OK":
                print("juhu")
        except ConnectionError:
            return

    @staticmethod
    def details() -> Any:
        details = CCSCraneDetails()
        details.event = CCSEvent(type=f"net.contargo.logistics.tams.details")
        details.feature = [
            CCSFeature(
                type=CCSFeatureType.FINAL_LANDING,
            )
        ]
        return dataclass_to_json(details), 200

    def shutdown(self) -> None:
        self.shutdown_event.set()
