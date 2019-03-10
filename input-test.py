from gpiozero import Button
from gpiozero import LED
from time import sleep

opensensor = Button(23)
closedsensor = Button(24)

def open_on():
    print('Open aan')
def open_off():
    print('Open uit')
def closed_on():
    print('Dicht aan')
def closed_off():
    print('Dicht uit')

opensensor.when_pressed = open_on
opensensor.when_released = open_off
closedsensor.when_pressed = closed_on
closedsensor.when_released = closed_off

print ('current state, open:',opensensor.is_active, 'closed:',closedsensor.is_active)



while True:
    pass