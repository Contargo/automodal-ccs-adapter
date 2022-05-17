import time
from threading import Thread, Event
from functools import partial
from typing import Optional

import snap7

from paho.mqtt.client import MQTT_ERR_SUCCESS, Client, MQTTv5
from paho.mqtt.properties import Properties

class MqttClient():
    def __init__(self) -> None:
        
        self.shutdown_event = Event()
        
        self.client = get_client_with_reconnect(
            client_id="mqtt_sps_bridge"
        )
        
        
        self.worker: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker.start()

    def worker(self):
        while not self.shutdown_event.is_set():
            pass
            time.sleep(5)

    def shutdown(self) -> None:
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

def _on_disconnect(
    client: Client,
    __: None,
    reason_code: int,
    ___: Properties
) -> None:
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