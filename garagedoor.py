import paho.mqtt.client as mqtt
from gpiozero import Button
from gpiozero import LED
from time import sleep

client = mqtt.Client()
relais = LED(18)
opensensor = Button(23)
closedsensor = Button(24)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("cmnd/pi-garage/relais")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    msg.payload = msg.payload.decode("utf-8")
    print(msg.topic+" "+str(msg.payload))
    if str(msg.payload) == "ON":
        relais.blink(1,1,1)
        client.publish("stat/pi-garage/relais", "OFF")
    else:
        print('Het is uit')

def open_on():
    client.publish("cmnd/pi-garage-open-closed/OPEN", "ON")
def open_off():
    client.publish("cmnd/pi-garage-open-closed/OPEN", "OFF")
def closed_on():
    client.publish("cmnd/pi-garage-open-closed/CLOSED", "ON")
def closed_off():
    client.publish("cmnd/pi-garage-open-closed/CLOSED", "OFF")

client.on_connect = on_connect
client.on_message = on_message

opensensor.when_pressed = open_on
opensensor.when_released = open_off
closedsensor.when_pressed = closed_on
closedsensor.when_released = closed_off

client.connect("192.168.3.1", 1883, 60)
client.loop_start()

while True:
    pass
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
