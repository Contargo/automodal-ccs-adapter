import time
from argparse import ArgumentParser
from logging import getLogger, WARNING, CRITICAL
from typing import Any

from mqtt.client import MqttClient
from sps.client import SpsClient
from sps.server import SpsServer
from ccs.ccs import CCS

def get_args() -> Any:
    parser = ArgumentParser(description="yolo")
    parser.add_argument(
        "-s",
        "--server",
        action="store_true", 
        help="start demo sps"
    )
    parser.add_argument(
        "-i",
        "--ip",
        type=str,
        default="127.0.0.1",
        help="start demo sps"
    )
    return parser.parse_args()

def run() -> None:
    args = get_args()
    getLogger("snap7").setLevel(CRITICAL)
    sps_server = SpsServer()
    sps_client = SpsClient(ip=args.ip)
    mqtt_client = MqttClient()
    ccs = CCS()
    sps_client.set_mqtt_queue(mqtt_client.queue)
    mqtt_client.set_sps_queue(sps_client.queue)
    try:
        if args.server:
            print("Start SERVER")
            sps_server.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mqtt_client.shutdown()
        sps_client.shutdown()
        sps_server.shutdown()
        ccs.shutdown()

if __name__ == "__main__":
    run()
