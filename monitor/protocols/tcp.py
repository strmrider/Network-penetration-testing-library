import struct
import socket


class TcpFlags:
    def __init__(self, flags_data):
        self.urg = flags & 0x0020
        self.ack = flags & 0x0010
        self.psh = flags & 0x0008
        self.rst = flags & 0x0004
        self.syn = flags & 0x0002
        self.fin = flags & 0x0001

    def __str__(self):
        return "====Flags====\n" \
               "URG: {}\n" \
               "ACK: {}\n" \
               "PSH: {}\n" \
               "RST: {}\n" \
               "SYN: {}\n" \
               "FIN: {}\n".format(self.urg, self.ack, self.psh, self.rst, self.syn, self.fin)


class TCP:
    def __init__(self, data):
        header = struct.unpack("!2H 2I 4H", data)
        self.src_port = header[0]
        self.dest_port = header[1]
        # sequence number
        self.sqe_number = header[2]
        # Acknowledgment number
        self.ack_number = header[3]
        self.data_offset = header[4] >> 12
        self.reserved = (header[4] >> 6) * 4
        self.flags = TcpFlags(header[4] & 0x003f)

        self.window_size = header[5]
        self.checksum = header[6]
        # urgent pointer
        self.urg_pointer = header[7]

    def __str__(self):
        return "====TCP Header====\n"\
               "Source port: {}\n" \
               "Destination port: {}\n" \
               "Sequence number: {}\n" \
               "Acknowledgment number: {}\n"\
               "Data offset: {}\n"\
                "Reserved: {}\n"\
                "Window size: {}\n"\
                "Checksum: {}\n"\
                "Urgent pointer: {}\n".format(self.src_port, self.dest_port, self.sqe_number, self.ack_number,
                                              self.data_offset, self.reserved, self.window_size, self.checksum,
                                              self.urg_pointer) + self.flags.__str__()

    def summary(self):
        return "Protocol: TCP Source port: {} Destination port: {}".format(self.src_port, self.dest_port)

