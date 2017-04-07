from brain.core.bbbgpio import UART, RS485
from common.messaging import Message, SerialPortController, robot
from threading import Thread
from queue import Empty

xbee_uart_port = "/dev/ttyO1"
bus_uart_port = "/dev/ttyO2"


class CHAMP(Thread):

    def __init__(self):
        Thread.__init__(self)

        bus_port = RS485(bus_uart_port, 9600, 0, de_pin_number=49, re_pin_number=115)
        xbee_port = UART(xbee_uart_port, 9600, 0)

        self.bus = SerialPortController(bus_port)
        self.xbee = SerialPortController(xbee_port)

        self.bus.start()
        self.xbee.start()

        self.running = True

    def process_user_message(self, message):
        """
        Kind of a switch case for handling the different kinds of commands coming from the user
        This is about is simple as it gets though, maybe it'll stay
        :param message: the message that is going to be processed
        :return: nothing
        """

        pass_through_commands = [
                                    robot.orange_gripper.rotate,
                                    robot.green_gripper.rotate,
                                    robot.abdomen.w_pp.set_extension,
                                    robot.abdomen.s_pp.set_extension,
                                    robot.abdomen.x_pp.set_extension
                                 ]

        if message in pass_through_commands:
            print("Passing through: " + str(message.get_verbose()))
        else:
            print("No handler set up for message: " + str(message.get_verbose()))

    def process_bus_message(self, message):
        pass

    def run(self):

        while self.running:

            try:  # get message from the xbee
                message_from_user = self.xbee.incoming_messages.get(False)
                self.process_user_message(message_from_user)
            except Empty:
                pass

            try:  # get message from the bus
                message_from_bus = self.bus.incoming_messages.get(False)
                self.process_bus_message(message_from_bus)
            except Empty:
                pass

if __name__ == "__main__":

    print("Starting Robot in BBB")

    c = CHAMP()

    c.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            c.xbee.running = False
            c.running = False
            c.xbee.join()
            c.join()
