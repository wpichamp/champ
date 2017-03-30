from core.bbbgpio import RS485

# for using the same port across different modules
bus_port = RS485("/dev/ttyO1", baudrate=115200, de_pin_number=60, re_pin_number=115)
