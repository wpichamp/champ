from core.bbbgpio import UART, pin
from threading import Thread
from time import sleep

uart = UART("/dev/ttyO2", 9600)
pin = pin(60, "out")

delay = 10

while True:

    incoming_bytes = uart.read_bytes(2)

    string = ""
    for byte in incoming_bytes:
        string += str(ord(byte)) + " "

    print(string)

    value = int(ord(incoming_bytes[1]))

    if value > 50:
        pin.set_output(1)
    else:
        pin.set_output(0)


