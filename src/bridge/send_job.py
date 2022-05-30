import requests

from ccs.helper import dataclass_to_json
from ccs.types import CCSJob

url = 'http://localhost:9999/job'

data = dataclass_to_json(CCSJob())

x = requests.post(url, json =data)

print(x.text)