import packet
import socket

MAX_RECEIVE_BYTES = 65565
LOCAL_HOST = 0

# protocols
TCP = 0
UDP = 1


class Filter:
    def __init__(self):
        self.values = []
        self.inclusion = True

    def is_included(self, value):
        return value in self.values

    def is_defined(self):
        return len(self.values) > 0

    def add(self, value):
        self.values.append(value)

    def add_list(self, values):
        self.values.extend(values)

    def remove(self, value):
        self.values.remove(value)

    def reset(self):
        self.values = []
        self.inclusion = True


class Filters:
    def __init__(self):
        self.src_ip = Filter()
        self.target_ip = Filter()
        self.src_mac = Filter()
        self.target_mac = Filter()
        self.protocol = Filter()
        self.at_least_one = True

    def set_filter_mode(self, mode):
        self.at_least_one = mode

    def is_filtered(self, packet):
        if self.at_least_one:
            return self.check_filter(packet.transport.source_ip, self.src_ip) or \
                   self.check_filter(packet.transport.dest_ip, self.target_ip) or \
                   self.check_filter(packet.ethernet.src_mac, self.src_mac) or \
                   self.check_filter(packet.ethernet.dest_mac, self.target_mac) or \
                   self.check_filter(packet.transport.protocol, self.protocol)
        else:
            return self.check_filter(packet.transport.source_ip, self.src_ip) and \
                   self.check_filter(packet.transport.dest_ip, self.target_ip) and \
                   self.check_filter(packet.ethernet.src_mac, self.src_mac) and \
                   self.check_filter(packet.ethernet.dest_mac, self.target_mac) and \
                   self.check_filter(packet.transport.protocol, self.protocol)

    def reset(self):
        self.src_ip.reset()
        self.target_ip.reset()
        self.src_mac.reset()
        self.target_mac.reset()
        self.protocol.reset()

    @staticmethod
    def check_filter(value, filter):
        if filter.is_defined():
            return filter.is_included(value)


class NetworkMonitor:
    def __init__(self, host):
        if host is not LOCAL_HOST:
            self.host = host
        else:
            self.host = socket.gethostname()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        self.run = False
        self.filters = Filters()
        self.packets = []
        # optional function (set by the user). Gets a Packet as a parameter and handles it
        self.packet_handler = None

    def set_packet_handler_func(self, handler_func):
        self.packet_handler = handler_func

    def capture_data(self, save_packets=True):
        self.run = True
        self.packets = []
        while self.run:
            captured_data = self.socket.recvfrom(MAX_RECEIVE_BYTES)
            unpacked_packet = packet.Packet(captured_data)
            if self.filters.is_filtered(unpacked_packet):
                if self.packet_handler:
                   self.packet_handler(unpacked_packet)
                if save_packets:
                    self.packets.append(packet.Packet(unpacked_packet))
        self.socket.close()

    def stop(self):
        self.run = False
