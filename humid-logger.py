import paho.mqtt.client as mqtt
import time
from bme280 import bme280


bme280.bme280_i2c.set_default_i2c_address(0x76)
bme280.bme280_i2c.set_default_bus(1)
bme280.setup()
while True:
    data = bme280.read_all()
    print(data)
    time.sleep(10)
