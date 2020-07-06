import socket
import threading
import Queue
import os

UDP = 0
TCP = 1
DEFAULT_TIMEOUT = 5
LOCAL_HOST = -1


class NetworkScanner:
    def __init__(self, network):
        self.socket = None
        self.queue = None
        self.ports = []
        self.pings = []
        if network:
            self.network = network
        else:
            self.network = socket.gethostbyname(socket.gethostname())
        self.timeout = DEFAULT_TIMEOUT

    def set_network(self, network):
        self.network = network

    def set_timeout(self, timeout):
        self.timeout = timeout

    # scan single port
    def scan_port(self, port):
        if self.socket.connect_ex((self.network, port)):
            return False
        else:
            return True

    def threader(self):
        while True:
            port = self.queue.get()
            if self.scan_port(port):
                self.ports.append(port)
            self.queue.task_done()

    def scan(self, protocol, ports_range=()):
        if protocol == UDP:
            proto = socket.SOCK_DGRAM
        elif protocol == TCP:
            proto = socket.SOCK_STREAM
        else:
            raise Exception("Incorrect protocol type")
        self.socket = socket.socket(socket.AF_INET, proto)
        self.queue = Queue.Queue()
        self.ports = []

        for x in range(100):
            thread = threading.Thread(target=self.threader)
            thread.daemon = True
            thread.start()

        for port in ports_range:
            self.queue.put(port)

        self.queue.join()
        self.socket.close()

        return self.ports

    def ping_ip(self, current_ip):
        response = os.popen("ping -n 1 " + current_ip)
        for line in response.readlines():
            if "Received = 1" in line:
                return True

        return False

    def ping_threader(self):
        while True:
            ip = self.queue.get()
            if self.ping_ip(ip):
                self.pings.append(ip)

            self.queue.task_done()

    def ping_sweep(self, ip_range):
        self.pings = []
        self.queue = Queue.Queue()
        local = self.network.split('.')
        ip_base = local[0] + '.' + local[1] + '.' + local[2] + '.'

        for x in range(100):
            thread = threading.Thread(target=self.ping_threader)
            thread.daemon = True
            thread.start()

        for ip in range(ip_range[0], ip_range[1]):
            self.queue.put(ip_base + str(ip))

        self.queue.join()
        return self.pings
