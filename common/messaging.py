from serial import Serial, SerialTimeoutException
from queue import Queue, Empty
from threading import Thread
from copy import deepcopy

message_size = 7
message_header_size = 5


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

    def __init__(self, port, decode_function, message_length):
        MessageTXRX.__init__(self)
        self.port = port
        self.running = True
        self.decode_function = decode_function
        self.message_length = message_length

    def run(self):
        incoming_message_bytes = []

        while self.running:

            try:
                message_to_send = self.outgoing_messages.get(False)
                print("Serial TX: " + str(message_to_send.get_verbose()))
                message_bytes = message_to_send.serialize()
                print(message_bytes)
                self.port.write(bytearray(message_bytes))
            except Empty:
                pass

            try:
                incoming_byte = self.port.read()  # this should just timeout, not block
                if len(incoming_byte) > 0:
                    formatted_byte = ord(incoming_byte)
                    incoming_message_bytes.append(formatted_byte)
                    if len(incoming_message_bytes) == self.message_length:
                        incoming_message = self.decode_function(incoming_message_bytes)
                        self.incoming_messages.put(incoming_message)
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


class Stacker(object):

    def __init__(self, id_number=None, name=None):
        self.name = name
        self.id_number = id_number
        self.prefex = []
        if id_number is not None:
            self.prefex = [id_number]

    def safe_add(self, incoming_item, items):
        for item in items:
            if item.id_number == incoming_item.id_number:
                raise ValueError(
                    "A message with the id: " + str(item.id_number) + " already exists.")
        incoming_item.name = self.name + "->" + incoming_item.name
        incoming_item.prefex = self.prefex + incoming_item.prefex
        items.append(incoming_item)
        return incoming_item


class Message(Stacker):

    def __init__(self, message_id=None, message_name=None):
        Stacker.__init__(self, message_id, message_name)
        self.payload = 0

    def set_payload(self, payload_value):
        self.payload = payload_value
        return self

    def serialize(self):
        buffer_length = message_header_size - len(self.prefex)
        buffer = []
        if buffer_length > 0:
            for x in range(buffer_length):
                buffer.append(0)
        else:
            buffer_length = 0

        full_message = self.prefex + buffer + [self.payload, len(self.prefex)]

        return full_message

    def get_verbose(self):
        verbose_string = "Name [" + str(self.name) + "]"
        verbose_string += " Payload [" + str(self.payload) + "]"
        verbose_string += " Serialized [" + str(self.serialize()) + "]"
        return verbose_string

    def get_copy(self):
        return deepcopy(self)


class MessageContainer(Stacker):

    def __init__(self, container_id=None, container_name=None):
        Stacker.__init__(self, container_id, container_name)
        self.sub_containers = []
        self.messages = []

    def add_sub_container(self, incoming_container):
        return self.safe_add(incoming_container, self.sub_containers)

    def add_message(self, incoming_message):
        return self.safe_add(incoming_message, self.messages)

    def get_all_messages(self):
        output = []
        output += self.messages
        self.get_messages(self, output)
        return output

    def get_messages(self, container, output):
        sub_containers = container.sub_containers
        for container in sub_containers:
            output += container.messages
            self.get_messages(container, output)


class RootContainer(object):

    def __init__(self, name):

        self.name = name

    def decode_message(self, message_list):
        depth = message_list[-1]
        payload = message_list[-2]
        header = message_list[0:depth]
        message_id = header[-1]

        current_container = self
        good_container = None
        found = False

        for header_id in header:

            for sub_container in current_container.sub_containers:
                if sub_container.id_number == header_id:
                    current_container = sub_container
                    break

            if current_container.id_number == header_id:
                good_container = current_container
                found = True

        if found:
            for message in good_container.messages:
                if message.id_number == message_id:
                    return message.set_payload(payload)

        raise ValueError("Message not found matching that stream")