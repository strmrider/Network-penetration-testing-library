import struct
import binascii
import socket


class EthernetHeader:
    def __init__(self, data):
        header = struct.unpack('!6s6sH', data[:14])
        self.dest_mac = binascii.hexlify(header[0])
        self.src_mac = binascii.hexlify(header[1])
        self.protocol = header[2] >> 8

    def __str__(self):
        return "====Ethernet====\n" \
               "Destination MAC: {}\n" \
               "source MAC: {}\n" \
               "protocol version: {}".format(self.dest_mac, self.src_mac, self.protocol)

    def summary(self):
        return "Destination MAC: {} source MAC: {}".format(self.dest_mac, self.src_mac)