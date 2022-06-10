from snap7.client import Client
from snap7.util import get_int, set_int

client = Client()
client.connect("10.192.0.150",0,0)

reading = client.db_read(4000, 0, 4)
print(get_int(reading,0))
print(get_int(reading,2))
set_int(reading,2,1337)

client.db_write(4000,0,reading)

reading = client.db_read(4000, 2, 2)
print(reading)
print(get_int(reading,0))
