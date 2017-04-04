from brain.core.bbbgpio import UART, RS485
from common.messaging import Message, command_container, SerialPortController
from threading import Thread
from queue import Empty

xbee_uart_port = "/dev/ttyO1"
bus_uart_port = "/dev/ttyO2"


class CHAMP(Thread):

    def __init__(self):
        Thread.__init__(self)

        xbee_port = UART(xbee_uart_port, 9600, 0)
        bus_port = RS485(bus_uart_port, 9600, 0, de_pin_number=49, re_pin_number=115)

        self.bus = SerialPortController(bus_port)
        self.xbee = SerialPortController(xbee_port)

        self.bus.start()
        self.xbee.start()

        self.running = True

    def process_user_message(self, message):
        """
        I don't really like the way this is handled, could do some kind of handler dictionary
        This is about is simple as it gets though, maybe it'll stay
        :param message: the message that is going to be processed
        :return: nothing
        """

        if message is command_container.grip_orange_gripper:
            print("grip the orange gripper!")
        elif message is command_container.grip_green_gripper:
            print("grip the green gripper")
        elif message is command_container.set_w_pp_extension:
            # print("set extension")
            output_message = Message(name="ToBus", command_id_number=0, payload=message.payload)
            self.bus.outgoing_messages.put(output_message)
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
