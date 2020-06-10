# Network-penetration-testing-library
A cybersecurity python library containing to Penetration testing and network traffic monitoring tools

# Features
## Port scanning
Scan for open ports per given protocol
```Python
import portscanner

scanner = portscanner.PortScanner()
# scan ports in given range and return a list with all the open ports
ports = scanner.scan(portscanner.LOCAL_HOST, portscanner.UDP, (1, 65500))
```
## Network traffic monitor
### Packets sniffing
The library unpacks the Physical layer (Ethrenet), Network layer (Ipv4, ICMP), Transport layer (UDP, TCP) and HTTP on Application layer.
```Python
import monitor

# gets a host machine to monitor
sniffer = monitor.NetworkMonitor(monitor.LOCAL_HOST)
sniffer.capture_data(save_packets=True)

# extract sniffed packets
captured_packets = sniffer.packets
```
#### Filters
#### Print packets

## Man in the middle (ARP spoofing)
### Attack
If an attack is succesful all the packets in the traffic between the victim and the gateway will be sniffed.
```Python
import mitm

# define a sniffed packet handler. It will run for every sniffed packet when attacking.
def packet_handler(packet):
  # simply print given packet
  print packet
  
# the code uses the local host as the attacker
m = mitm.MitM()
# set gateway's and victm's MAC aand ip addresses
gateway= ('c91f05bc4c59', '93.120.174.77')
victim= ('7aab539606eb', '58.88.156.2')

m.set_targets(victim, gateway)
m.attack(save_packets=True, packet_handler_func=packet_handler)
# sniffed packets are printed...
```
### Detection
An attempt to detect ARP spoofing attack by scanning Ip and MAC addresses duplications in ARP cache table.
```Python
arp_table = mitm.get_arp_table()
# returns suspected ip addresses
suspects = mitm.scan_table(arp_table)
```
## Website Footprinting
## Denial-of-Service
### Attack
### Detection
