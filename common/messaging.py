from serial import Serial, SerialTimeoutException
from queue import Queue, Empty
from threading import Thread
from time import sleep
from random import randint
from copy import deepcopy


class Message(object):

    def __init__(self, name=None, command_id_number=None, takes_input=False, payload=0, incoming_bytes=None):
        self.name = name
        self.command_id_number = command_id_number
        self.takes_input = takes_input
        self.payload = payload

    def set_payload(self, payload):
        """
        Value should be filtered here, like if you want to take the input and multiply it by 10 before it goes out
        By default, it converts the value to an int
        :param payload:
        :return:
        """

        try:
            value = int(payload)
        except ValueError as e:
            print("Bad conversion, error [" + str(e) + "]")

        self.payload = value
        return self  # very important for automatic operation generation

    def serialize(self):
        values = [int(self.command_id_number), int(self.payload)]
        return bytearray(values)

    def get_verbose(self):
        verbose_string = "Name [" + str(self.name) + "]"
        verbose_string += " Command ID number [" + str(self.command_id_number) + "]"
        verbose_string += " Takes Input [" + str(self.takes_input) + "]"
        verbose_string += " Payload [" + str(self.payload) + "]"

        if self.takes_input:
            verbose_string += " Payload [" + str(self.payload) + "]"

        return verbose_string

    def get_copy(self):
        return deepcopy(self)


class MessageTXRX(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.incoming_messages = Queue()  # filled with messages
        self.outgoing_messages = Queue()

    def transmit_message(self, message):
        message_text = message.get_verbose()
        print("TX: " + message_text)

    def run(self):
        while True:
            try:
                message_to_send = self.outgoing_messages.get(False)
                self.transmit_message(message_to_send)
            except Empty:
                pass


class SerialPortController(MessageTXRX):

    def __init__(self, port):
        MessageTXRX.__init__(self)
        self.port = port
        self.running = True

    def transmit_message(self, message):
        print("Transmitting Message Over Serial: " + str(message.get_verbose()))
        message_bytes = message.serialize()
        self.port.write(message_bytes)

    def run(self):
        number_of_bytes_per_message = command_container.bytes_per_message
        incoming_message_bytes = []

        while self.running:

            try:
                message_to_send = self.outgoing_messages.get(False)
                self.transmit_message(message_to_send)
            except Empty:
                pass

            try:
                incoming_byte = self.port.read()  # this should just timeout, not block
                if len(incoming_byte) > 0:
                    incoming_message_bytes.append(incoming_byte)
                    if len(incoming_message_bytes) == number_of_bytes_per_message:
                        self.incoming_messages.put(command_container.decode_message_bytes(incoming_message_bytes))
                        incoming_message_bytes = []
            except SerialTimeoutException:
                pass


class MessagePasser(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.message_queue = Queue()
        self.add_to_partner = self.bad_add_to_partner
        self.name = None

    def bad_add_to_partner(self, message):
        raise NotImplementedError("This must get reset")

    def set_partner_add_to_queue_method(self, method):
        self.add_to_partner = method

    def run(self):
        while True:
            message = self.message_queue.get()
            print("In [" + self.name + "] Message: " + message.name)
            if message.takes_input:
                print("Payload: " + str(message.value))


class CommandClass(object):

    rotate_orange_gripper = Message("Rotate Orange Gripper", 0, True)
    rotate_green_gripper = Message("Rotate Green Gripper", 1, True)
    set_w_pp_extension = Message("Set W PP Extension", 2, True)
    set_s_pp_extension = Message("Set S PP Extension", 3, True)
    set_x_pp_extension = Message("Set X PP Extension", 4, True)
    send_bytes_to_bus = Message("Send Bytes To Bus", 5, True)
    grip_orange_gripper = Message("Grip Orange Gripper", 6)
    grip_green_gripper = Message("Grip Green Gripper", 7)
    send_bytes_to_payload = Message("Send Bytes To Payload", 8, True)

    command_dict = {}  # this gets filled in the constructor

    command_list = [
        rotate_orange_gripper,
        rotate_green_gripper,
        set_w_pp_extension,
        set_s_pp_extension,
        set_x_pp_extension,
        send_bytes_to_bus,
        grip_green_gripper,
        grip_orange_gripper,
        send_bytes_to_payload
    ]

    bytes_per_message = 2

    def __init__(self):
        for outer_command in self.command_list:
            for inner_command in self.command_list:
                if outer_command is not inner_command:
                    if outer_command.command_id_number == inner_command.command_id_number:
                        exception_message = "You can't have two commands with the same ID! "
                        exception_message += str(inner_command.name) + " Has the same ID as: " + str(outer_command.name) + " of [" + str(outer_command.command_id_number) + "]"
                        raise Exception(exception_message)

        for command in self.command_list:
            self.command_dict[command.command_id_number] = command

    def decode_message_bytes(self, message_bytes):
        message_type = ord((message_bytes[0]))
        message_data = ord((message_bytes[1]))
        message = self.command_dict[message_type]
        message.set_payload(message_data)
        return message


command_container = CommandClass()
