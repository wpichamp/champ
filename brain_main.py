from brain.core.bbbgpio import UART
from common.messaging import Message, command_container, XbeeController
from threading import Thread
from queue import Empty

xbee_uart_port = "/dev/ttyO1"


class CHAMP(Thread):

    def __init__(self):
        Thread.__init__(self)
        port = UART(xbee_uart_port, 9600)
        self.xbee = XbeeController(port)
        self.xbee.start()
        self.running = True

    def run(self):
        while self.running:
            try:
                message = self.xbee.incoming_messages.get(False)
                print(message.get_verbose())
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
