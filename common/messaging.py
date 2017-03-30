from serial import Serial
from queue import Queue, Empty
from threading import Thread


class Message(object):

    def __init__(self, name=None, command_id_number=None, takes_input=False, incoming_bytes=None):
        self.name = name
        self.command_id_number = command_id_number
        self.takes_input = takes_input
        self.payload = None

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

        self.payload = payload
        return self  # very important for automatic operation generation

    def serialize(self):
        values = [int(self.command_id_number)]
        if self.takes_input:
            values.append(int(self.payload))
        print(values)
        return bytearray(values)

    def get_verbose(self):
        verbose_string = "Name [" + str(self.name) + "]"
        verbose_string += " Command ID number [" + str(self.command_id_number) + "]"
        verbose_string += " Takes Input [" + str(self.takes_input) + "]"

        if self.takes_input:
            verbose_string += " Payload [" + str(self.payload) + "]"

        return verbose_string


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

    def __init__(self):
        for outer_command in self.command_list:
            for inner_command in self.command_list:
                if outer_command is not inner_command:
                    if outer_command.command_id_number == inner_command.command_id_number:
                        exception_message = "You can't have two commands with the same ID! "
                        exception_message += str(inner_command.name) + " Has the same ID as: " + str(outer_command.name) + " of [" + str(outer_command.command_id_number) + "]"
                        raise Exception(exception_message)


class MessageTXRX(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.incoming_messages = Queue()  # filled with messages
        self.outgoing_messages = Queue()

    def send_message(self, message):
        self.outgoing_messages.put(message)

    def __transmit_message__(self, message):
        message_text = message.get_verbose()
        print("Transmitting: " + message_text)

    def run(self):
        while True:
            try:
                message_to_send = self.outgoing_messages.get(False)
                self.__transmit_message__(message_to_send)
            except Empty:
                pass


class XbeeController(MessageTXRX):

    def __init__(self, port, baud_rate):
        MessageTXRX.__init__(self)
        self.port = Serial(port=port, baudrate=baud_rate)

    def __transmit_message__(self, message):
        """
        Do something with the xbee
        :param message:
        :return:
        """
        message_bytes = message.serialize()
        self.port.write(message_bytes)
