from machine import Pin
import time 

button = Pin(13, Pin.IN, Pin.PULL_UP)
led = Pin(25, Pin.OUT)

def read_button(button):
    if not button.value():
        print(1)
        time.sleep(0.01) # check state at 100Hz (higher than camera anyways)
        led.value(1)
    else:
        print(0)
        time.sleep(0.01)
        led.value(0)

try:
    while True:
        read_button(button)
    
except:
    pass
