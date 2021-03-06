from serial import Serial, SerialTimeoutException
from queue import Queue, Empty
from threading import Thread
from copy import deepcopy


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

        incoming_message_bytes = bytearray()

        while self.running:

            try:
                message_to_send = self.outgoing_messages.get(False)
                print("Serial TX: " + str(message_to_send.get_verbose()))
                message_bytes = message_to_send.serialize()
                self.port.write(message_bytes)
            except Empty:
                pass

            try:
                incoming_byte = self.port.read()  # this should just timeout, not block
                if len(incoming_byte) > 0:
                    incoming_message_bytes += incoming_byte
                    if len(incoming_message_bytes) > 0:
                        if len(incoming_message_bytes) == self.message_length:
                            try:
                                incoming_message = self.decode_function(incoming_message_bytes)
                                self.incoming_messages.put(incoming_message)
                            except ValueError or OSError as e:
                                # something has gone wrong with the transmission
                                # reset the input buffer of the port
                                print("problem with transmission: [" + str(e) + "]")
                                pass

                            # self.incoming_messages.put(incoming_message)
                            incoming_message_bytes = bytearray()
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


class MessageCommon(object):
    def __init__(self, id_number, name):
        self.id_number = id_number
        self.name = name

    def search_for_matching_id(self, incoming_item, items):
        for item in items:
            if item.id_number == incoming_item.id_number:
                raise ValueError(
                    "A message with the id: " + str(item.id_number) + " already exists.")


class Message(MessageCommon):

    def __init__(self, message_id, message_name):
        MessageCommon.__init__(self, message_id, message_name)
        self.prefex = [message_id]
        self.payload = 0
        self.message_header_size = None

    def set_payload(self, payload_value):
        self.payload = payload_value
        return self

    def serialize(self):
        buffer_length = self.message_header_size - len(self.prefex)

        buffer = []
        if buffer_length > 0:
            for x in range(buffer_length):
                buffer.append(0)

        full_message = self.prefex + buffer + [self.payload, len(self.prefex)]
        print(full_message)
        message_bytes = bytearray(full_message)
        checksum = sum(message_bytes)  # pythonic way to do checksums, good enough for me
        message_bytes.append(checksum)

        return message_bytes

    def get_verbose(self):
        verbose_string = "Name [" + str(self.name) + "]"
        verbose_string += " Payload [" + str(self.payload) + "]"
        verbose_string += " Serialized [" + str(self.serialize()) + "]"
        return verbose_string

    def get_copy(self):
        return deepcopy(self)


class AbstractContainer(MessageCommon):

    def __init__(self, container_id, container_name, max_depth=None, remaining_depth=None):
        MessageCommon.__init__(self, container_id, container_name)

        self.sub_containers = []

        self.max_depth = max_depth
        self.remaining_depth = remaining_depth
        self.sub_layer_occupied = False

    def modify_depth(self):
        if self.sub_layer_occupied is False:
            self.remaining_depth -= 1
            if self.remaining_depth < 0:
                raise ValueError("The tree is too deep!")
            self.sub_layer_occupied = True

    def add_sub_container(self, incoming_container):
        self.search_for_matching_id(incoming_container, self.sub_containers)
        incoming_container.name = self.name + "->" + incoming_container.name
        self.sub_containers.append(incoming_container)
        self.modify_depth()
        incoming_container.remaining_depth = self.remaining_depth
        incoming_container.max_depth = self.max_depth
        return incoming_container


class MessageContainer(AbstractContainer):

    def __init__(self, container_id, container_name):
        AbstractContainer.__init__(self, container_id, container_name)
        self.prefex = [container_id]
        self.messages = []

    def add_message(self, incoming_message):
        self.search_for_matching_id(incoming_message, self.messages)
        incoming_message.name = self.name + "->" + incoming_message.name
        incoming_message.prefex = self.prefex + incoming_message.prefex
        self.messages.append(incoming_message)
        incoming_message.message_header_size = self.max_depth
        return incoming_message

    def add_sub_container(self, incoming_container):
        self.search_for_matching_id(incoming_container, self.sub_containers)
        incoming_container.name = self.name + "->" + incoming_container.name
        self.sub_containers.append(incoming_container)
        self.modify_depth()
        incoming_container.prefex = self.prefex + incoming_container.prefex
        incoming_container.remaining_depth = self.remaining_depth
        incoming_container.max_depth = self.max_depth
        return incoming_container

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


class RootContainer(AbstractContainer):

    def __init__(self, container_name, max_depth):
        AbstractContainer.__init__(self, 0, container_name, max_depth=max_depth, remaining_depth=max_depth)
        self.remaining_depth = max_depth
        self.message_length = max_depth + 3

    def pre_process_incoming_bytes(self, incoming_bytes):
        checksum = incoming_bytes[-1]
        other_part_of_message = incoming_bytes[0:-1]

        good_checksum = (checksum == sum(other_part_of_message))

        if not good_checksum:
            raise OSError("The checksum has failed, there is something wrong with the hardware")

        output = []
        for incoming_byte in incoming_bytes:
            output.append((incoming_byte))
        return output


    def decode_message(self, incoming):
        message_list = self.pre_process_incoming_bytes(incoming)

        # print("Message List: " + str(message_list))
        checksum = message_list[-1] # shouldn't be used, broken out for debugging purposes.
        depth = message_list[-2]
        payload = message_list[-3]

        header = message_list[0:depth]
        message_id = header[-1]

        """
        print("Checksum: " + str(checksum))
        print("Depth: " + str(depth))
        print("Payload: " + str(payload))
        print("Header: " + str(header))
        print("Message ID: " + str(message_id))
        """

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

    def get_all_messages(self):
        output = []
        for container in self.sub_containers:
            output += container.get_all_messages()
        return output