import time
from argparse import ArgumentParser
from logging import getLogger, CRITICAL
from typing import Any

from bridge.logger.logger import Logger
from bridge.tams.tams import CCS
from bridge.sand.bridge import SandBridge
from bridge.sps.client import SpsClient
from bridge.sps.server import SpsServer
from bridge.web.web import Web


def get_args() -> Any:
    parser = ArgumentParser(description="yolo")
    parser.add_argument("--server", action="store_true", help="start demo SPS")
    parser.add_argument("--ccs", action="store_true", help="start ccs")
    parser.add_argument("--sand", action="store_true", help="start sand bridge")
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="IP of SPS")
    parser.add_argument("-l", "--log", action="store_true", help="log to csv")
    return parser.parse_args()


def run() -> None:
    args = get_args()
    print(f"{args=}")
    getLogger("snap7").setLevel(CRITICAL)
    sps_server = SpsServer()
    sps_client = SpsClient(ip_address=args.ip)
    web = Web(sps_client)
    sand_bridge = SandBridge(sps_client)
    ccs = CCS(sps_client)
    logger = Logger(sps_client)
    try:
        if args.server:
            print("Start SERVER")
            sps_server.start()
        sps_client.connect()
        sps_client.update_data() # just to be sure client_data read from an inialized bytearray
        sps_client.start()
        if args.ccs:
            print("Start CCS")
            ccs.start()
        if args.sand:
            print("Start SAND BRIDGE")
            sand_bridge.start()
        web.start()
        if args.log:
            logger.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sand_bridge.shutdown()
        sps_client.shutdown()
        sps_server.shutdown()
        ccs.shutdown()
        logger.shutdown()

if __name__ == "__main__":
    run()
