from brain.core.bbbgpio import UART, RS485
from common.messaging import Message, SerialPortController
from common.robot_topology import robot
from threading import Thread
from queue import Empty, Queue

xbee_uart_port = "/dev/ttyO1"
bus_uart_port = "/dev/ttyO2"

class BusModule(object):

    def __init__(self):
        self.outgoing_messages = Queue()
        self.incoming_messages = Queue()

class BusController(Thread):

    orange_gripper = BusModule()
    green_gripper = BusModule()
    abdomen = BusModule()

    bus_modules = [
        orange_gripper,
        green_gripper,
        abdomen
    ]

    def __init__(self, port, decode_function, message_length):
        Thread.__init__(self)
        self.decode_function = decode_function
        self.message_length = message_length
        self.port = port

    def run(self):
        while True:
            for bus_module in self.bus_modules:
                try:
                    message_to_send = bus_module.outgoing_messages.get(False)
                    message_bytes = message_to_send.serialize()
                    self.port.write(bytearray(message_bytes))

                    # read in response from module as well

                    """
                    incoming_message_bytes = self.port.read(self.message_length)
                    incoming_message = self.decode_function(incoming_message_bytes)
                    bus_module.incoming_messages.put(incoming_message)
                    """
                except Empty:
                    pass

class CHAMP(Thread):

    def __init__(self, robot_topography):
        Thread.__init__(self)

        self.robot_topography = robot_topography

        bus_port = RS485(bus_uart_port, 9600, 0, de_pin_number=49, re_pin_number=115)
        xbee_port = UART(xbee_uart_port, 9600, 0)

        self.bus = BusController(bus_port, robot_topography.decode_message, robot_topography.message_length)

        self.xbee = SerialPortController(xbee_port, robot_topography.decode_message, robot_topography.message_length)

        self.bus.start()
        self.xbee.start()

        self.running = True

    def process_message_from_oi(self, message):
        """
        Kind of a switch case for handling the different kinds of commands coming from the user
        This is about is simple as it gets though, maybe it'll stay
        :param message: the message that is going to be processed
        :return: nothing
        """

        if message in self.robot_topography.abdomen.get_all_messages():
            self.bus.abdomen.outgoing_messages.put(message)
        else:
            print("No handler set up for message: " + str(message.get_verbose()))

    def process_message_from_bus(self, message):
        pass

    def run(self):

        while self.running:

            try:  # get message from the xbee
                message_from_user = self.xbee.incoming_messages.get(False)
                self.process_message_from_oi(message_from_user)
            except Empty:
                pass

            # get messages from the bus

if __name__ == "__main__":

    print("Starting Robot in BBB")

    c = CHAMP(robot)

    c.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            c.xbee.running = False
            c.running = False
            c.xbee.join()
            c.join()
