from threading import Thread
from queue import Queue





class CHAMP(Thread):

    def __init__(self):
        Thread.__init__(self)


    def run(self):
        while True:
            print("get message")