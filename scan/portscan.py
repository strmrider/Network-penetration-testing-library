import socket, threading, queue

UDP = 0
TCP = 1
DEFAULT_TIMEOUT = 5
LOCAL_HOST = -1

class PortScanner:
    def __init__(self, network_ip):
        self.network_ip = network_ip
        self.timeout = DEFAULT_TIMEOUT
        self.ports = []
        self.queue = None

    def scan_port(self, port, protocol):
        connection = socket.socket(socket.AF_INET, protocol)
        response = not connection.connect_ex((self.network_ip, port))
        connection.close()

        return response

    def __scan_threader(self, protocol, output):
        while True:
            port = self.queue.get()
            if self.scan_port(port, protocol):
                self.ports.append(port)
                if output:
                    print (str(port) + " is open")
            self.queue.task_done()

    def scan(self, protocol, ports_range=(), output=False):
        if protocol == UDP:
            proto = socket.SOCK_DGRAM
        elif protocol == TCP:
            proto = socket.SOCK_STREAM
        else:
            raise Exception("Incorrect protocol type")

        if len(ports_range) <= 0:
            ports_range = (0, 65535)
        self.queue = queue.Queue()
        self.ports = []

        for x in range(100):
            thread = threading.Thread(target=self.__scan_threader, args=(proto,output,))
            thread.daemon = True
            thread.start()

        for port in range(ports_range[0], ports_range[1]):
            self.queue.put(port)

        self.queue.join()

        return self.ports