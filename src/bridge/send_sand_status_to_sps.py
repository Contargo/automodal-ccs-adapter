from argparse import ArgumentParser
from typing import Any

from snap7.client import Client
from snap7.util import get_int, set_int

from bridge.sps.data import get_item_with_name


def get_args() -> Any:
    parser = ArgumentParser(description="")
    parser.add_argument("-s", "--stop", action="store_true", help="start demo SPS")
    parser.add_argument("--spsip", type=str, default="127.0.0.1", help="IP of SPS")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print(f"{args=}")
    client = Client()
    client.connect(args.spsip, 0, 0)

    item = get_item_with_name("SandStatus")
    if args.stop:
        client.db_write(item.dbnumber, item.start, bytearray(b"\x01"))
        print("wrote 0x01 in SandStatus")
    else:
        client.db_write(item.dbnumber, item.start, bytearray(b"\x00"))
        print("wrote 0x00 in SandStatus")
