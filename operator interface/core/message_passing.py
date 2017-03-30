from threading import Thread
from queue import Queue
from random import randint
from time import sleep
from messages import Message


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




