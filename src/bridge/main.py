import time
from argparse import ArgumentParser
from logging import CRITICAL, getLogger
from typing import Any

from bridge.logger.logger import Logger
from bridge.sand.bridge import SandBridge
from bridge.sps.client import SpsClient
from bridge.sps.server import SpsServer
from bridge.tams.tams import CCS
from bridge.web.web import Web


def get_args() -> Any:
    parser = ArgumentParser(description="yolo")
    parser.add_argument("--server", action="store_true", help="start demo SPS")
    parser.add_argument("--ccs", action="store_true", help="start ccs")
    parser.add_argument("--sand", action="store_true", help="start sand bridge")
    parser.add_argument("--spsip", type=str, default="127.0.0.1", help="IP of SPS")
    parser.add_argument("--mqttip", type=str, default="localhost", help="IP of mqtt broker for sand feature")
    parser.add_argument("-l", "--log", action="store_true", help="log metrics to csv")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose console logging")
    parser.add_argument("--logwebcalls", action="store_true", help="log web calls")
    return parser.parse_args()


def run() -> None:
    args = get_args()
    print(f"[MAIN] {args=}")
    getLogger("snap7").setLevel(CRITICAL)
    sps_server = SpsServer()
    sps_client = SpsClient(ip_address=args.spsip)
    web = Web(sps_client, args.verbose)
    sand_bridge = SandBridge(sps_client, args.mqttip, args.verbose)
    ccs = CCS(sps_client, verbose=args.verbose)
    logger = Logger(sps_client)
    if not args.logwebcalls:
        print("[MAIN] disable werkzeug logging")
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    try:
        if args.server:
            print("[MAIN] Start SERVER")
            sps_server.start()
        sps_client.connect()
        sps_client.update_data()  # just to be sure client_data read from an inialized bytearray
        sps_client.start()
        if args.ccs:
            print("[MAIN] Start CCS")
            ccs.start()
        if args.sand:
            print("[MAIN] Start SAND BRIDGE")
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
