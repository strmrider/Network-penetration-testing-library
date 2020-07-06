import struct


class UDP:
    def __init__(self, data):
        header = struct.unpack("!4H", data[:8])
        self.src_port = header[0]
        self.dst_port = header[1]
        self.length = header[2]
        self.checksum = header[3]

    def __str__(self):
        return "====UDP Header===="\
                "Source port: {}\n"\
                "Destination port: {}\n"\
                "Length: {}\n"\
                "Checksum: {}\n".format(self.src_port, self.dst_port, self.length, self.checksum)

    def summary(self):
        return "Source port: {} Destination port: {}".format(self.src_port, self.dst_port)