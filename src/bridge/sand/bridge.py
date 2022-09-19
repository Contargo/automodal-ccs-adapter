import pickle
import time
from functools import partial
from threading import Event, Thread

from paho.mqtt.client import MQTT_ERR_SUCCESS, Client, MQTTv5
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from bridge.sps.client import SpsClient
from bridge.sps.types import spsbyte, spsdint, spsint, spsreal
from bridge.util.types import MQTT_Payload, MQTT_Topic

class SandBridge:
    def __init__(self, sps_client: SpsClient) -> None:

        self.sps_client = sps_client
        self.shutdown_event = Event()
        self.status = True
        self.old_Status = False

        self.client = get_client_with_reconnect(client_id="mqtt_sps_bridge")
        self.client.connect("localhost")
        self.client.on_message = self.on_collision_update
        self.client.subscribe("+/+/data/collision")
        self.client.loop_start()
        self.worker_thread: Thread = Thread(
            target=self.worker,
            args=(),
            name="sps worker",
            daemon=True,
        )
        self.worker_status_thread: Thread = Thread(
            target=self.worker_status,
            args=(),
            name="sps worker status",
            daemon=True,
        )

    def start(self) -> None:
        self.worker_thread.start()
        self.worker_status_thread.start()


    def on_collision_update(self, _client, _: MQTT_Topic, msg: MQTT_Payload) -> None:
        # todo: payload format. Aktuell nur ein Bool ob danger or not
        try:
            print(pickle.loads(msg.payload))
            if pickle.load(msg.payload):
                self.status = True
            else:
                self.status = False
         except pickle.UnpicklingError:

    def worker_status(self) -> None:
        time.sleep(1)
        while not self.shutdown_event.is_set():
            if self.status != self.old_Status:
                self.old_Status = self.status
                if self.status:
                    self.sps_client.write_item("SandStatus", spsbyte(b"\x01"))
                else:
                    self.sps_client.write_item("SandStatus", spsbyte(b"\x00"))
            time.sleep(0.3)

    def worker(self) -> None:
        publish_properties = Properties(PacketTypes.PUBLISH)
        # to make sure we can pickle everything and make it easier here, performance here is irrelevant
        publish_properties.UserProperty = ("datatype", "pickle")

        old_katz = 0
        old_crane = 0
        old_spreader = 0
        histerese = 50  # 5 cm

        while not self.shutdown_event.is_set():
            katz = self.sps_client.read_value("CraneCoordinatesY", spsdint) 
            crane = self.sps_client.read_value("CraneCoordinatesX", spsdint) 
            spreader = self.sps_client.read_value("CraneCoordinatesZ", spsdint) 
            group = "katze"

            # for us we need only changes on the katz value
            if abs(old_katz - katz) > histerese: # type: ignore
                self.client.publish(
                    topic=f"bridge/{group}/data/position",
                    payload=pickle.dumps(
                        {
                            "y_position": katz,
                            "x_position": crane,
                            "z_position": spreader,
                        }
                    ),
                    properties=publish_properties,
                )
            time.sleep(0.5)

    def shutdown(self) -> None:
        print("MQTT_CLIENT: shutdown")
        self.shutdown_event.set()
        self.worker_thread.join()
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
