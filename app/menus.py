from . import style
from .consts import OpCommands
import sys
sys.path.append('/home/stormrider/.local/lib/python3.8/site-packages')
from tabulate import tabulate

general = [('scan', 'Scan network for information'),
           ('dos', 'DoS (Denial of Service) and DDoS attacks'),
           ('mitm', 'Man in the middle attacks')]

scan_options = [(OpCommands.PORT_SCAN, 'network(ip), protocol(tcp/udp)', 'Port scanning. Look up for open ports'),
                (OpCommands.PING_SWEEP, 'network(ip)', 'Scan for available machines in a given network'),
                (OpCommands.SNIFFER, '', 'Network packets sniffer'),
                (OpCommands.SCAN_IP, 'occurrences, timeout', 'Scan for exceptional occurrences of an IP addresses'),
                (OpCommands.SCAN_ARP, '', "Scan machine's ARP table for exceptional occurrences of an IP addresses"),
                (OpCommands.FOOTPRINT, 'url', "Web server footprint: http methods and headers"),
                (OpCommands.BANNER_GRAB, 'url', "Web server footprint: banner grabbing")]

mitm_options = [(OpCommands.ARP_SPOOFING, '', 'ARP cache poisoning'),
                (OpCommands.DNS_POISONING, 'server ip', 'DNS server poisoning'),
                ('dhcp', '', 'DHCP attack')]

dos_options = [(OpCommands.TCP_FLOOD, 'target(ip), port, timeout', 'TCP flood attack'),
               (OpCommands.SYN_FLOOD, 'target(ip), port, timeout', 'TCP SYN flood attack'),
               (OpCommands.UDP_FLOOD, 'target(ip), port, timeout', 'UDP flood attack'),
               (OpCommands.PING_OF_DEATH, 'target(ip), timeout', 'Ping of Death attack'),
               (OpCommands.SMURF_ATTACK, 'target(ip), timeout', 'Smurf attack'),
               (OpCommands.HTTP_FLOOD, 'target(ip), port, timeout', 'HTTP flood attack'),
               (OpCommands.SLOWLORIS, 'target(ip), port, requests, timeout', 'SlowLoris attack')]
COMMAND = 0
DESCRIPTION = 1


def print_main_menu():
    print(style.fg.lightgrey, tabulate(general, headers=["Option", "Description"]))

def print_options(options):
    print("")
    print(style.fg.lightgrey, tabulate(options, headers=["Command", "Parameters", "Description"]))
    print("")