from snap7.client import Client
from snap7.util import get_int

client = Client()
client.connect("10.192.0.150",0,3)
reading = client.db_read(4000, 0, 4)
print(get_int(reading,0))