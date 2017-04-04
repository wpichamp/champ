from brain.core.bbbgpio import UART, RS485
from common.messaging import Message, command_container, XbeeController
from threading import Thread
from queue import Empty

xbee_uart_port = "/dev/ttyO1"
bus_uart_port = "/dev/ttyO2"


class CHAMP(Thread):

    def __init__(self):
        Thread.__init__(self)
        xbee_port = UART(xbee_uart_port, 9600)
        self.xbee = XbeeController(xbee_port)

        self.bus = RS485(bus_uart_port, 9600, 49, 117)

        self.xbee.start()



        self.running = True

    def process_message(self, message):
        print("Process Message: " + str(message.get_verbose()))

        if message is command_container.grip_orange_gripper:
            print("grip the orange gripper!")
        elif message is command_container.grip_green_gripper:
            print("grip the green gripper")
        elif message is command_container. set_w_pp_extension:
            print("set extension")
        else:
            print("No handler is set up for that command")

    def run(self):
        while self.running:
            try:
                message = self.xbee.incoming_messages.get(False)
                self.process_message(message)
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
