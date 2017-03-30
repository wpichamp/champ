from serial import Serial

good_pins = [48, 49, 117, 115, 20, 60, 112, 66, 69, 45, 47, 27, 67, 68, 44, 26, 46, 65, 61]
pin_types = ["in", "out"]
states = [0, 1]
uarts = {"/dev/ttyO1" : "BB-UART1", "/dev/ttyO2" : "BB-UART2"}


class pin(object):

    def __init__(self, pin_name, config_state):

        self.type = None

        if pin_name not in good_pins:
            raise Exception("That's a bad pin, try a different one")

        self.pin_name = pin_name

        try:
            with open("/sys/class/gpio/export", "w") as file:
                file.write(str(pin_name))
        except IOError as e:
            if "busy" not in str(e):
                raise IOError(e)

        self.config(config_state)

    def config(self, type):

        if type not in pin_types:
            raise Exception("That's a valid pin mode, try a in our out")

        self.type = type

        with open("/sys/class/gpio/gpio" + str(self.pin_name) + "/direction" , "w") as file:
            file.write(type)


    def set_output(self, state):

        if self.type is None:
            raise Exception("You must configure the pin first")

        if state not in states:
            raise Exception("Not a valid state")

        with open("/sys/class/gpio/gpio" + str(self.pin_name) + "/value" , "w") as file:
            file.write(str(state))


class UART(object):

    def __init__(self, name, baudrate):

        try:
            with open("/sys/devices/bone_capemgr.9/slots", "w") as file:
                file.write(uarts[name])
        except IOError as e:
            if "File exists" not in str(e):
                raise IOError(e)

        port = Serial(name, baudrate=baudrate)
        port.open()

        self.port = port

    def write_bytes(self, bytes):
        self.port.write(bytes)

    def read_bytes(self, num_bytes):
        return self.port.read(num_bytes)


class RS485(UART):

    def __init__(self, name, baudrate, de_pin_number, re_pin_number):
        super(RS485, self).__init__(name, baudrate)

        de = pin(de_pin_number, "out")
        re = pin(re_pin_number, "out")

        self.de_pin = de
        self.re_pin = re

    def __set_tx_mode__(self):
        self.de_pin.set_output(1)
        self.re_pin.set_output(1)

    def __set_rx_mode__(self):
        self.de_pin.set_output(0)
        self.re_pin.set_output(0)

    def write(self, bytes):
        self.__set_tx_mode__()
        self.write_bytes(bytes)

    def read(self, num_bytes):
        self.__set_rx_mode__()
        return self.read_bytes(num_bytes)



