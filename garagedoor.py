# Garage door opener in Python for Raspberry PI
# 2 reed switches: one at beginning of motor rail and one at end of rail
# 1 relais to mimic a button press to open or close the door
# Communication with openHAB2 using MQTT.
import paho.mqtt.client as mqtt
import time, sched, logging, sys
from gpiozero import Button, DigitalOutputDevice

# Set the default pin factory to a mock factory

# Use logging
logging.basicConfig(stream=sys.stderr, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

# Timer to check if garagedoor opens or closes in time
# Event is triggered when maxmovetime is exceeded
movetimer=sched.scheduler()
pingtimer=sched.scheduler()

mtevent=False
ptevent=False
maxmovetime=30
pingtime=600 # 10 minutes

# Define in and outputs
relais = DigitalOutputDevice(18,initial_value=True, active_high=True)
opensensor = Button(23)
closedsensor = Button(24)

# Garage door closed:  open sensor not active  && closed sensor active
# Garage door open:    open sensor  active     && closed sensor not active
# Garage door moving:  open sensor not active  && closed sensor not active, move time not passed 
# Both sensors active: something is broken
def is_open() :
    return opensensor.is_active and not closedsensor.is_active

def is_closed() :
    return not opensensor.is_active and closedsensor.is_active

def is_moving() :
    return not opensensor.is_active and not closedsensor.is_active

def is_broken() :
    return opensensor.is_active and closedsensor.is_active


#Define mqqt client
client = mqtt.Client()
mqtthost = "192.168.3.1"
mqttstate = "cmnd/pi-garage-state"
mqttcommand = "cmnd/pi-garage/relais"
mqttcommandstat = "stat/pi-garage/relais"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.debug("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mqttcommand)

# The callback for when a PUBLISH message is received from the server.
# Handling commands given by the server
def on_message(client, userdata, msg):
    msg.payload = msg.payload.decode("utf-8")
    logging.debug(msg.topic+" "+str(msg.payload))
    if str(msg.payload) == "ON":
        relais.off()
        logging.info('Relais Off')
        time.sleep(1)      
        relais.on()
        logging.info('Relais On')
        client.publish(mqttcommandstat, "OFF")
    else:
        logging.info('Off command reveiced')

# The call back if the door has been moving for too long: set state to unknown
def traveltimer_passed():
    global mtevent
    logging.info('Move timer  passed')
    mtevent=False
    if is_moving() or is_broken():
        logging.debug('State is UNKNOWN')
        client.publish(mqttstate, "UNKNOWN")

def pingtimer_passed():
    global ptevent
    logging.info('Ping timer  passed')
    ptevent=False
    if is_open():
        logging.info('Ping: Door is OPEN')
        client.publish(mqttstate, "OPEN")
    elif is_closed():
        logging.info('Ping: Door is CLOSED')
        client.publish(mqttstate, "CLOSED")
    ptevent=movetimer.enter(pingtime,1,pingtimer_passed) # Trigger new ping timer
    logging.debug("Ping Timer started "+str(ptevent))

# The call back if one of the inputs changes: determine the state of the door
def determine_state():

    global mtevent
    logging.debug('current state, open: %s closed: %s',opensensor.is_active,closedsensor.is_active)
    if is_open():
        if mtevent:
            movetimer.cancel(mtevent) # Cancel timer, status is known
        logging.info('Door is OPEN')
        client.publish(mqttstate, "OPEN")
    elif is_closed():
        logging.info('Door is CLOSED')
        if mtevent:
            movetimer.cancel(mtevent) # Cancel timer, status is known
        client.publish(mqttstate, "CLOSED")
    elif is_moving:
        logging.info('Door is Moving')    
        client.publish(mqttstate, "MOVING")
        mtevent=movetimer.enter(maxmovetime,1,traveltimer_passed) # Door moving start time
        logging.debug(mtevent)
    else:
        client.publish(mqttstate, "UNKNOWN")

# Register  callbacks
client.on_connect = on_connect
client.on_message = on_message
opensensor.when_activated = determine_state
opensensor.when_deactivated = determine_state
closedsensor.when_activated = determine_state
closedsensor.when_deactivated = determine_state

# Connect mqtt
client.connect(mqtthost, 1883, 60)
client.loop_start()
determine_state()
pingtimer_passed()
while True:
    movetimer.run()
    pingtimer.run()
