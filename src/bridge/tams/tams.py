import time
from random import random
from threading import Event, Thread
from typing import Any

import requests
from flask import Flask, request
from requests import ConnectionError

from bridge.sps.client import SpsClient
from bridge.sps.data import db_items
from bridge.sps.enums import SPSStatus
from bridge.sps.types import spsbool, spsbyte, spsdint, spsint
from bridge.tams.enums import CCSFeatureType, CCSJobType, CCSJobStatus
from bridge.tams.helper import dataclass_to_json, generate_feature, generate_metadata
from bridge.tams.job import CCSJobState, _JobState
from bridge.tams.types import (
    CCSCraneDetails,
    CCSEvent,
    CCSFeature,
    CCSMetric,
    CCSMetricEntry,
)


class CCS:
    locaton: str = "terminal"
    type: str = "crane"
    name: str = "PSKran"

    def __init__(
        self,
        sps_client: SpsClient,
        tams_url: str = "http://localhost:9998",
        verbose: bool = False,
    ):
        self.verbose = verbose
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

        self.worker_metric: Thread = Thread(
            target=self.metric,
            args=(),
            name="Metric Worker",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_rest.start()
        self.worker_sps.start()
        self.worker_metric.start()

    def add_endpoints(self) -> None:
        self.app.add_url_rule(
            "/job_cancel", "job_cancel", self.job_cancel, methods=["POST"]
        )
        self.app.add_url_rule("/job", "job_post", self.job_post, methods=["POST"])
        self.app.add_url_rule("/job", "job_get", self.job_get, methods=["GET"])
        self.app.add_url_rule("/details", "details", self.details, methods=["GET"])

    def rest(self) -> None:
        self.app.run(host="0.0.0.0", port=9999)

    def sps(self) -> None:
        old_value = spsint(255)
        while not self.shutdown_event.is_set():
            value = self.sps_client.read_value("JobStatus", spsbyte)
            if value != old_value:
                old_value = value
                print(f"[TAMS][sps worker] {old_value=}, {value=}")
                if self.sps_client.read_value("JobStatusDone", spsbool):
                    print("[TAMS][sps worker] JobStatusDone")
                    self.state.job_done()
                self.send_status()
            time.sleep(1)

    def metric(self) -> None:
        while not self.shutdown_event.is_set():
            self.send_metric()
            time.sleep(1)

    def job_cancel(self, *args, **kwargs) -> Any:  # type: ignore
        self.state.job_done()
        print("[TAMS][job_cancel] called")
        self.sps_client.write_item("JobCommand", spsbyte(b"\x01"))
        return "OK", 200

    def job_post(self, *args, **kwargs) -> Any:  # type: ignore
        ret = self.state.set_new_job(request.data.decode("utf-8"))
        job = self.state.get_job()
        sps_done = self.sps_client.read_value("JobStatusDone", spsbool)
        if ret == "invalid":
            return job, 405
        if ret == "has job" or not sps_done:
            return "", 409
        if job is not None:
            print("[TAMS][job_post] send new job to SPS")
            if job.type == CCSJobType.PICK:
                self.sps_client.write_item("JobType", spsbyte(b"\x01"))
            if job.type == CCSJobType.DROP:
                self.sps_client.write_item("JobType", spsbyte(b"\x02"))
            self.sps_client.write_item("JobCoordinatesX", spsdint(job.target.x))
            self.sps_client.write_item("JobCoordinatesY", spsdint(job.target.y))
            self.sps_client.write_item("JobCoordinatesZ", spsdint(job.target.z))
            self.sps_client.write_item("JobBay", spsdint(job.target_logical.bay))
            self.sps_client.write_item("JobRow", spsdint(job.target_logical.row))
            self.sps_client.write_item("JobTier", spsdint(job.target_logical.tier))
            self.sps_client.write_item("JobSpreaderSize", spsint(20))
            self.sps_client.write_item("JobNewJob", spsint(1))
        print(f"[TAMS][job_post] {job=}")
        return "OK", 200

    def job_get(self) -> Any:
        if self.state.has_job():
            return self.state.get_job_as_json(), 200
        else:
            return "no job", 404

    def send_status(self) -> None:
        try:
            ret = requests.post(
                f"{self.tams_url}/state", data=self.state.get_state_as_json()
            )
            # if ret.text == "OK":
            #    print("send status successfull")
        except (ConnectionError, ConnectionRefusedError):
            return

    def send_alarm(self) -> None:
        try:
            ret = requests.post(f"{self.tams_url}/alarm", json={})
            if ret == "OK":
                print("[TAMS][send_alarm] ok")
        except ConnectionError:
            return

    def send_metric(self) -> None:
        try:
            metrics = CCSMetric()
            metrics.event = CCSEvent(type=f"net.contargo.logistics.tams.metric")
            for item in db_items:
                value = self.sps_client.read_value(item.name, item.type)
                metrics.metrics.append(
                    CCSMetricEntry(
                        name=item.name, datatype=item.type.__name__, value=value
                    )
                )
            ret = requests.post(
                f"{self.tams_url}/metric", json=dataclass_to_json(metrics)
            )
            if ret == "OK":
                if self.verbose:
                    print("[TAMS][send_metric] ok")
        except ConnectionError:
            return

    @staticmethod
    def details() -> Any:
        details = CCSCraneDetails()
        details.event = CCSEvent(type=f"net.contargo.logistics.tams.details")
        details.features = [
            CCSFeature(
                type=CCSFeatureType.FINAL_LANDING,
            )
        ]
        return dataclass_to_json(details), 200

    def shutdown(self) -> None:
        self.shutdown_event.set()
