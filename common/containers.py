class Stacker(object):

    def __init__(self, id_number=None, name=None):
        self.name = name
        self.id_number = id_number
        self.prefex = []
        if id_number is not None:
            self.prefex.append(id_number)

    def thing(self, incoming_item, items):
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
        return self.prefex + [self.payload]


class MessageContainer(Stacker):

    def __init__(self, container_id=None, container_name=None):
        Stacker.__init__(self, container_id, container_name)
        self.sub_containers = []
        self.messages = []

    def add_sub_container(self, incoming_container):
        return self.thing(incoming_container, self.sub_containers)

    def add_message(self, incoming_message):
        return self.thing(incoming_message, self.messages)

    def reconstruct_message(self, message_list):
        message_header = message_list[0:-2]
        message_id = message_list[-2:-1].pop()
        message_payload = message_list[-1:].pop()

        containers = self.sub_containers

        found = False
        good_container = None
        for id_number in message_header:
            for container in containers:
                if id_number == container.id_number:
                    good_container = container
                    found = True
                    break
            if found:
                for message in good_container.messages:
                    if message.id_number == message_id:
                        message.set_payload(message_payload)
                        return message

        raise ValueError("Message not found matching that stream")

robot = MessageContainer(container_name="CHAMP")
robot.orange_gripper = robot.add_sub_container(MessageContainer(0, "Orange Gripper"))
robot.green_gripper = robot.add_sub_container(MessageContainer(1, "Green Gripper"))
robot.orange_gripper.grip = robot.orange_gripper.add_message(Message(0, "Grip"))
robot.orange_gripper.ungrip = robot.orange_gripper.add_message(Message(1, "Un grip"))

message_array = robot.orange_gripper.ungrip.set_payload(255).serialize()
print(message_array)
m = robot.reconstruct_message(message_array)
print(m.name)



