# Network-penetration-testing-library
A cybersecurity library containing penetration testing and network traffic monitoring tools

# Features
## Network scanner
### Port scanning
Scan network for open ports per given protocol
```Python
import scanner

network_scanner = scanner.NetworkScanner(scanner.LOCAL_HOST)
# scan ports in given range and return a list with all the open ports
ports = scanner.scan(portscanner.LOCAL_HOST, portscanner.UDP, (1, 65500))
```
### Ping sweep
Detection of other available machines in a network
```Python
# receives a range of ip addresses on the network and returns a list of the active addresses
ip_addr = scanner.ping_sweep((1,255))
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
Filter packets by protocols and source/target IP and MAC addresses.
```Python
# add ip filter
sniffer.filters.src_ip.add('93.120.174.77')
# protocol filter
sniffer.filter.protocol.add(sniffer.TCP)
# add list
mac_adrrs = ['c91f05bc4c59', 'a81f08bc9d54']
sniffer.filters.target_mac.add_list(mac_adrrs)
```
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
Perform tests on HTTP servers by analyzing the responses.
Test server's responses to HTTP methods
```Python
import footprint

url = "http://google.com"
print footprint.check_http_methods(url)
# output
[('GET', 200, 'OK'), ('POST', 405, 'Method Not Allowed'), ('PUT', 405, 'Method Not Allowed'), ('DELETE', 405, 'Method Not Allowed'), ('OPTIONS', 405, 'Method Not Allowed'), ('TEST', 405, 'Method Not Allowed'), ('TRACE', 405, 'Method Not Allowed')]
```
Test server's headers list
```Python
print footprint.check_http_header(url)
# output
[('Server', 'gws'), ('Date', 'Thu, 11 Jun 2020 01:06:21 GMT'), ('Via', 'No details'), ('X-Powered-By', 'No details'), ('X-Country-Code', 'No details'), ('Connection', 'No details'), ('Content-Length', '5817')]
```
## Denial-of-Service
### Attack
### Detection
