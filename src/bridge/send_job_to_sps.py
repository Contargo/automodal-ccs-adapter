import requests

from bridge.tams.helper import dataclass_to_json
from bridge.tams.types import CCSJob

url = "http://localhost:80/job"  # pylint: disable=invalid-name

data = CCSJob().to_json()  # type: ignore[attr-defined]

x = requests.post(url, json=data)

print(x.text)
