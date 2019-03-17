# Data logger, using BME280 sensor to measure air-pressure, temperature and humidity \
# and send it as json data using mqtt

import paho.mqtt.client as mqtt
import time, json, logging, sys
from bme280 import bme280

# Data from bme280: humidity, pressure, temperature
id_h = 0
id_p = 1
id_t = 2


# Use logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

client = mqtt.Client()
mqtthost = "192.168.3.1"
mqtttopic = "stat/pi-logger"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Logger started. MQTT connected with result code "+str(rc))


bme280.bme280_i2c.set_default_i2c_address(0x76)
bme280.bme280_i2c.set_default_bus(1)
bme280.setup()

client.connect(mqtthost, 1883, 60)
client.loop_start()

while True:
    data = bme280.read_all()
    datajson=json.dumps({'humidity' : data[id_h], 'pressure' : data[id_h], 'temperature':data[id_t]})
    logging.debug("Measurement data send:"+str(datajson))
    client.publish(mqtttopic,payload=datajson)
    time.sleep(60)
