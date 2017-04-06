from brain.core.bbbgpio import Pin, RS485
from time import sleep
from timeit import timeit

bus_uart_port = "/dev/ttyO2"
bus_port = RS485(bus_uart_port, 9600, 0, de_pin_number=49, re_pin_number=115)

values = []
for x in range(1000):
    values.append(255)
    execution_time = timeit(lambda: bus_port.write(bytearray(values)), number=1)

    line = str(execution_time)

    with open("ex_time.txt", "a") as the_file:
        the_file.write(line + '\n')
    print(line)
