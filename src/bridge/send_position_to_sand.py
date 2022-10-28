import pickle
from argparse import ArgumentParser
from typing import Any

from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from bridge.sand.bridge import get_client_with_reconnect


def get_args() -> Any:
    parser = ArgumentParser(description="")
    parser.add_argument("sensor_group", type=str)
    parser.add_argument("x_value", type=int)
    parser.add_argument("y_value", type=int)
    parser.add_argument("z_value", type=int)
    parser.add_argument(
        "--mqttip",
        type=str,
        default="localhost",
        help="IP of mqtt broker for sand feature",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose console logging"
    )
    return parser.parse_args()


def main() -> Any:
    args = get_args()
    client = get_client_with_reconnect(client_id="mqtt_sps_bridge")
    client.connect(args.mqttip)
    publish_properties = Properties(PacketTypes.PUBLISH)
    publish_properties.UserProperty = ("datatype", "pickle")

    if args.verbose:
        print(f"sensor group: {args.sensor_group}")
        print(f"x position: {args.x_value}")
        print(f"y position: {args.y_value}")
        print(f"z position: {args.z_value}")
        print(publish_properties)

    client.publish(
        topic=f"bridge/{args.sensor_group}/data/position",
        payload=pickle.dumps(
            {
                "y_position": args.y_value,
                "x_position": args.x_value,
                "z_position": args.z_value,
            }
        ),
        properties=publish_properties,
    )

    client.disconnect()


main()
