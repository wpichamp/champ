from brain.core.bbbgpio import Pin
from time import sleep

pin1 = Pin(49, "out")
pin2 = Pin(115, "out")


while True:
    print("on")
    pin1.set_output(1)
    pin2.set_output(1)
    sleep(1)
    print("off")
    pin1.set_output(0)
    pin2.set_output(0)
    sleep(1)