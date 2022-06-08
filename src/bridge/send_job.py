import requests

from bridge.ccs.helper import dataclass_to_json
from bridge.ccs.types import CCSJob

url = "http://localhost:9999/job"  # pylint: disable=invalid-name

data = dataclass_to_json(CCSJob())

x = requests.post(url, json=data)

print(x.text)
