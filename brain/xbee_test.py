from brain.core.bbbgpio import UART, Pin
from threading import Thread
from time import sleep

uart = UART("/dev/ttyO2", 9600)
pin = Pin(60, "out")

delay = 10
while True:
    print("writing bytes")
    uart.write_bytes(bytearray([0, 2, 4]))
    sleep(.01)

while True:

    print("Listening on: " + str(uart.port.name))

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


