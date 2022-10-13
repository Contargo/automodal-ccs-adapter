import json
from os import getcwd
from pathlib import Path
from threading import Event, Thread
from typing import Any

from flask import Flask, render_template, request
from flask_cors import CORS

from bridge.sps.client import SpsClient


class Web:
    locaton: str = "terminal"
    type: str = "crane"
    name: str = "PSKran"

    def __init__(self, sps_client: SpsClient, verbose: bool = False):
        self.sps = sps_client
        self.verbose = verbose
        template_folder = Path(__file__).parent.joinpath("template")
        static_folder = Path(__file__).parent.joinpath("assets")
        self.shutdown_event = Event()
        self.app = Flask(
            "tams web",
            root_path=getcwd(),
            template_folder=template_folder.as_posix(),
            static_folder=static_folder.as_posix(),
        )
        CORS(self.app)
        self.add_endpoints()
        self.worker_rest: Thread = Thread(
            target=self.rest,
            args=(),
            name="CCS Worker",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_rest.start()

    def add_endpoints(self) -> None:
        self.app.add_url_rule("/", "frontend", self.frontend, methods=["get"])
        self.app.add_url_rule("/body", "body", self.body_content, methods=["get"])

    def rest(self) -> None:
        self.app.run(host="0.0.0.0", port=8000)

    def frontend(self, *args, **kwargs) -> Any:  # type: ignore
        return render_template("empty_body.html")

    def body_content(self, *args, **kwargs) -> Any:  # type: ignore
        return render_template("body.html", sps_data=self.sps.get_table())

    def shutdown(self) -> None:
        self.shutdown_event.set()
