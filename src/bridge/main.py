import time

from mqtt.client import MqttClient
from sps.client import SpsClient
from sps.server import SpsServer


def run() -> None:
    sps_server = SpsServer()
    sps_client = SpsClient()
    mqtt_client = MqttClient()
    while True:
        time.sleep(1)
    

if __name__ == "__main__":
    run()
