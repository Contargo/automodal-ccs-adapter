import time
from argparse import ArgumentParser
from logging import getLogger, CRITICAL
from typing import Any

from bridge.ccs.ccs import CCS
from bridge.sand.bridge import SandBridge
from bridge.sps.client import SpsClient
from bridge.sps.server import SpsServer


def get_args() -> Any:
    parser = ArgumentParser(description="yolo")
    parser.add_argument("--server", action="store_true", help="start demo SPS")
    parser.add_argument("--ccs", action="store_true", help="start ccs")
    parser.add_argument("--sand", action="store_true", help="start sand bridge")
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="IP of SPS")
    return parser.parse_args()


def run() -> None:
    args = get_args()
    getLogger("snap7").setLevel(CRITICAL)
    sps_server = SpsServer()
    sps_client = SpsClient(ip_address=args.ip)
    sand_bridge = SandBridge(sps_client)
    ccs = CCS(sps_client)
    try:
        if args.server:
            print("Start SERVER")
            sps_server.start()
        if args.ccs:
            ccs.start()
        if args.sand:
            sand_bridge.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sand_bridge.shutdown()
        sps_client.shutdown()
        sps_server.shutdown()
        ccs.shutdown()


if __name__ == "__main__":
    run()
