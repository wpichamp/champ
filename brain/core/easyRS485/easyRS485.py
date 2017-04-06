from brain.core.easyRS485.commands import Message


class Command(object):

    def __init__(self, command_id):
        self.command_id = command_id


class CommandGroup(object):

    def __init__(self, group_id=None):
        self.group_id = group_id


class CHAMPCommands(CommandGroup):

    orange_gripper = CommandGroup(0)
    orange_gripper.grip = Command(1)


class Network(object):

    def __init__(self, port):
        self.port = port
        self.modules = []

    def add_module(self, module):

        for current_module in self.modules:
            if current_module.network_id is module.network_id:
                raise Exception("You can't add a node with the ID: " + str(module.network_id) + " it already exists.")

        self.modules.append(module)

    def send_message(self, message):
        message_bytes = message.serialize()
        self.port.write(message_bytes)
        m = Message(self.port.read(10))
        return m


class Module(object):

    def __init__(self, network, network_id):

        self.network_id = network_id
        self.network = network

    def send_message(self, message):
        self.tag_message(message)
        return self.network.send_message(message)

    def tag_message(self, message):
        message.to_id = self.network_id


