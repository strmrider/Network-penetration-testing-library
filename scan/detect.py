from inet.layers import Types, Packet
import socket, time, os, select

def detect_exceptional_ip(max_count, timeout=None):
    """
    Attempts to detect a DoS attack by detecting exceptional occurrences of IP addresses
    """
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 8)
    s.setblocking(0)
    ip_counter = {}
    start_time = time.time()
    exceptions = []
    inputs = [s]
    while True:
        if timeout and time.time() - start_time >= timeout:
            break
        r, w, e = select.select(inputs, [], inputs, 0)
        if s in r:
            packet_data = s.recvfrom(2048)
            ip_header = Packet(packet_data)[Types.Layers.IP]
            ip = socket.inet_ntoa(ip_header.source_ip)
            if ip in ip_counter:
                ip_counter[ip] += 1
                if ip_counter[ip] >= max_count:
                    exceptions.append(ip)
            else:
                ip_counter[ip] = 1

    return exceptions

def get_arp_table():
    table = []
    with os.popen('arp -a') as f:
        table_lines = f.readlines()
        for line in table_lines:
            line = str(line).split(' ')
            table.append((line[3], line[1].replace('(', '').replace(')', '')))

    return table

def scan_arp_table(arp_table=None):
    """
    Attempts to detect ARP poisoning by detecting exceptional occurrences of an IP addresses on the machine's ARP table
    """
    if not arp_table:
        arp_table = get_arp_table()
    suspects = {}
    for first_counter, record in enumerate(arp_table):
        mac = record[0]
        if mac in suspects:
            continue
        ip_addresses = []
        for second_counter, item in enumerate(arp_table):
            if mac == item[1] and first_counter is not second_counter:
                ip_addresses.append(item[1])

        if len(ip_addresses) > 0:
            ip_addresses.append(record[1])
        suspects[mac] = ip_addresses

    return suspects.keys()


def set_static_entry(ip, mac):
    command = "arp -s {} {}".format(ip, mac)
    os.system('cmd /c {}'.format(command))