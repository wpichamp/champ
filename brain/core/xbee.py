from serial import Serial
from bbbgpio import UART

xbee = UART("/dev/ttyO2", 9600)

count = 0

while True:

    rx = ord(xbee.read_bytes(1))

    if rx is 255:
        count += 1
        if count > 255:
            count = 0

    tx = [count]

    xbee.write_bytes(bytearray(tx))

    print "RX: " + str(rx) + " TX: " + str(tx)






