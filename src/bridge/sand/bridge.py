import json
import time
from collections import deque
from threading import Thread, Event, Lock
from functools import partial
from typing import Deque, Optional, Union, List

from paho.mqtt.client import MQTT_ERR_SUCCESS, Client, MQTTv5
from paho.mqtt.properties import Properties

from sps.client import SpsClient
from sps.enums import SPSClientQueueMSGs
from util.types import Position, MQTT_Topic, MQTT_Payload, SpsQueueItem, MqttQueueItem


class SandBridge:
    def __init__(self, sps_client: SpsClient) -> None:

        self.sps_client = sps_client
        self.shutdown_event = Event()

        self.client = get_client_with_reconnect(client_id="mqtt_sps_bridge")

        self.client.message_callback_add("+/+/data/status", self.on_status_update)
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        
    def start(self):
        self.worker.start()

    def set_sps_queue(self, queue: deque):
        self.sps_client_queue: Deque = queue

    def on_status_update(self, _: MQTT_Topic, payload: MQTT_Payload) -> None:
        # todo: payload format. Aktuell nur ein Bool ob danger or not
        if self.sps_client_queue is not None:
            if isinstance(payload, str):
                self.sps_client_queue.append(SpsQueueItem("status", bool(payload)))

    def worker(self):
        while not self.shutdown_event.is_set():
            time.sleep(1)

    def shutdown(self) -> None:
        print("MQTT_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker.join()
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()


def get_client_with_reconnect(
    client_id: str = "",
    protocol: int = MQTTv5,
) -> Client:
    client = Client(client_id=client_id, protocol=protocol)
    client.on_disconnect = partial(_on_disconnect)
    return client


def _on_disconnect(client: Client, __: None, reason_code: int, ___: Properties) -> None:
    print(  # allowed
        f"reason_code: {reason_code} | "  # pylint: disable=protected-access
        f"MQTT_ERR_SUCCESS: {MQTT_ERR_SUCCESS} | "
        f"client_id: {client._client_id}"
    )
    if reason_code != MQTT_ERR_SUCCESS:
        print(
            f"communicator client: '{client._client_id}' "  # pylint: disable=protected-access
            "got disconnected, retrying...",
            "__on_disconnect",
        )
        client.reconnect()
