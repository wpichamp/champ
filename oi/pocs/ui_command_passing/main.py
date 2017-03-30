from threading import Thread
from queue import Queue
from random import randint
from time import sleep


class Message(object):

    def __init__(self, text):
        self.text = text


class MessagePasser(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.message_queue = Queue()
        self.add_to_partner = None
        self.name = None

    def set_partner_add_to_queue_method(self, method):
        self.add_to_partner = method

    def run(self):
        while True:
            message = self.message_queue.get()
            print("In [" + self.name + "] Message: " + message.text)


class Ui(MessagePasser):

    def __init__(self):
        MessagePasser.__init__(self)
        self.name = "ui"


class Robot(MessagePasser):

    def __init__(self):
        MessagePasser.__init__(self)
        self.name = "robot"

if __name__ == "__main__":

    robot = Robot()
    ui = Ui()

    robot.set_partner_add_to_queue_method(ui.message_queue.put)
    ui.set_partner_add_to_queue_method(robot.message_queue.put)

    robot.start()
    ui.start()

    while True:

        random_number = randint(0, 10)

        if random_number == 5:
            robot.add_to_partner(Message("Hello from robot"))
        elif random_number == 1:
            ui.add_to_partner(Message("Hello from UI"))
        else:
            sleep(.5)




