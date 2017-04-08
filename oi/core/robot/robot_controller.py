from common.messaging import MessagePasser, MessageTXRX, SerialPortController
from queue import Empty
from serial import Serial


class Robot(MessagePasser):

    def __init__(self, robot_topology):
        MessagePasser.__init__(self)
        self.name = "robot"
        self.xbee = SerialPortController(Serial(port="COM21", baudrate=9600, timeout=0.01), robot_topology.decode_message, robot_topology.message_length)
        self.xbee.start()

    def process_message(self, message):
        print("Got new message: " + message.get_verbose())

    def run(self):

        while True:

            try:
                # try and get messages from the UI to pass to the robot
                message = self.message_queue.get(False)
                self.xbee.outgoing_messages.put(message)

            except Empty:
                # no new messages to send to the robot
                pass

            try:
                # get latest message from xbee
                incoming_message = self.xbee.incoming_messages.get(False)
                self.process_message(incoming_message)
            except Empty:
                # no new messages from the robot
                pass