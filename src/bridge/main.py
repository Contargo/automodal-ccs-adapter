import time

from src.bridge.mqtt.client import MqttClient
from src.bridge.sps.client import SpsClient
from src.bridge.sps.server import SpsServer


def run() -> None:
    sps_server = SpsServer()
    sps_client = SpsClient()
    mqtt_client = MqttClient()
    while True:
        time.sleep(1)
    

if __name__ == "__main__":
    run()
