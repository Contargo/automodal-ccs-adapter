import pickle
import sys

from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from bridge.sand.bridge import get_client_with_reconnect

client = get_client_with_reconnect(client_id="mqtt_sps_bridge")
client.connect("10.192.0.11")
publish_properties = Properties(PacketTypes.PUBLISH)
publish_properties.UserProperty = ("datatype", "pickle")

print(f"sensor group: {sys.argv[1]}")
print(f"x position: {sys.argv[2]}")
print(publish_properties)

client.publish(
    topic=f"bridge/{sys.argv[1]}/data/position",
    payload=pickle.dumps(
        {
            "y_position": 0,
            "x_position": sys.argv[2],
            "z_position": 0,
        }
    ),
    properties=publish_properties
)

client.disconnect()