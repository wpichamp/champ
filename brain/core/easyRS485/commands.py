command_name_to_type = {"GetStatus": 0}


class Message(object):
    def __init__(self, incoming=None):

        if incoming is None:
            self.to_id = 0
            self.from_id = 0
            self.checksum = None
            self.message_type = 0

            self.d0 = 0
            self.d1 = 0
            self.d2 = 0
            self.d3 = 0
            self.d4 = 0
            self.d5 = 0

        else:
            self.to_id = ord(incoming[0])
            self.from_id = ord(incoming[1])
            self.checksum = ord(incoming[2])
            self.message_type = ord(incoming[3])

            self.d0 = ord(incoming[4])
            self.d1 = ord(incoming[5])
            self.d2 = ord(incoming[6])
            self.d3 = ord(incoming[7])
            self.d4 = ord(incoming[8])
            self.d5 = ord(incoming[9])

    def __set_checksum__(self):
        self.checksum = 0

    def serialize(self):
        self.__set_checksum__()
        array = [self.to_id, self.from_id, self.checksum, self.message_type, self.d0, self.d1, self.d2, self.d3, self.d4, self.d5]
        # print array
        return bytearray(array)


class GetStatus(Message):

    def __init__(self, incoming=None):
        super(GetStatus, self).__init__(incoming)
