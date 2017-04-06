class Message(object):

    def __init__(self, message_group_id, message_id):
        self.message_group_id = message_group_id
        self.message_id = message_id
        self.d0 = 0
        self.d1 = 0
        self.d2 = 0
        self.d3 = 0
        self.d4 = 0
        self.d5 = 0
        self.d6 = 0
        self.d7 = 0

    def set_value(self, value):
        self.value = value


class MessageGroup(object):

    def __init__(self, group_id=None):
        self.group_id = group_id






commands = CHAMPCommands()

grip = commands.orange_gripper.grip.set_value(255)

print(grip.command_id)