from inet.layers import Types
from inet.packet import Packet
import socket, select

EQUAL = 0
NOT_EQUAL = 1
MAX_RECEIVE_BYTES = 65565


def default_packet_handler(packet):
    print (packet)


class FilterItem:
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

    def check(self, packet_value):
        if self.operator == EQUAL:
            return self.value == packet_value
        else:
            return self.value != packet_value


class Filter:
    def __init__(self):
        self.filter_items = []

    def is_valid(self, value):
        if not self.is_defined():
            return False
        for item in self.filter_items:
            if not item.check(value):
                return False
        return True

    def is_defined(self):
        return len(self.filter_items) > 0

    def add(self, item):
        self.filter_items.append(item)

    def add_list(self, items):
        self.filter_items.extend(items)

    def remove(self, item):
        self.filter_items.remove(item)

    def reset(self):
        self.filter_items = []


class Filters:
    def __init__(self):
        self.src_ip = Filter()
        self.dest_ip = Filter()
        self.src_mac = Filter()
        self.dest_mac = Filter()
        self.protocol = Filter()

    def is_filtered(self, packet):
        layers = packet.get_layers()
        for layer in layers:
            if not self.protocol.is_valid(layer.type):
                return False

        if Types.Layers.IP in packet:
            ip_layer = packet[Types.Layers.IP]
            if not (self.src_ip.is_valid(ip_layer.src_ip) and self.dest_ip.is_valid(ip_layer.dest_ip)):
                return False
        if Types.Layers.Ethernet in packet:
            ethernet_layer = packet[Types.Layers.Ethernet]
            if not (self.src_ip.is_valid(ethernet_layer.src_mac) and self.dest_ip.is_valid(ethernet_layer.dest_mac)):
                return False

        return True

    def reset(self):
        self.src_ip.reset()
        self.dest_ip.reset()
        self.src_mac.reset()
        self.dest_mac.reset()
        self.protocol.reset()

class SniffedPacket(Packet):
    def __init__(self, data):
        Packet.__init__(self)
        self.parse(data)

class Sniffer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
        self.filters = Filters()
        self.packets = []
        self.__run = False
        self.__packet_handler = default_packet_handler

    def capture_packet(self):
        print ("waiting for packets")
        captured = self.socket.recvfrom(MAX_RECEIVE_BYTES)
        packet = SniffedPacket(captured[0])
        self.__packet_handler(packet)
        if self.filters.is_filtered(packet):
            if self.__packet_handler:
                self.__packet_handler(packet)

    def start(self, packet_handler=None):
        self.packets = []
        if packet_handler:
            self.__packet_handler = packet_handler
        inputs = [self.socket]
        self.__run = True
        while self.__run:
            readable, writeable, error = select.select(inputs, [self.socket], inputs, 1)
            if self.socket in readable:
                self.capture_packet()

    def stop(self):
        self.__run = False

    def close(self):
        self.stop()
        self.socket.close()
