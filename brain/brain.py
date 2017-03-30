

class Command(object):

    def __init__(self):
        pass


class SetGripCommand(Command):

    def __init__(self, state):
        Command.__init__(self)
        self.state = state


class RobotModule(object):

    def __init__(self, bus, module_id):
        self.bus = bus
        self.module_id = module_id

        self.sensors = {}

    def send_command(self, command):
        self.bus.transmit_command(command, self.module_id)  # this should block

    def get_state(self):
        my_sensors = []

        for sensor in my_sensors:
            self.sensors[sensor] = sensor.get_state()


class Gripper(RobotModule):

    def __init__(self, bus, module_id):
        RobotModule.__init__(self, bus, module_id)

        self.gripped = False

    def grip(self):

        if self.gripped is False:
            self.send_command(SetGripCommand(True))

    def release_grip(self):

        if self.gripped is True:
            self.send_command(SetGripCommand(False))


class Robot(object):

    def __init__(self):
