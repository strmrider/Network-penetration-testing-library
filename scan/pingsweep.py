import os, platform, threading, queue

class PingSweep:
    """
    Scanning for available machine's un a given network
    """
    def __init__(self, network_ip):
        self.network_ip = network_ip
        self.pings = None
        self.queue = None
        self.os = platform.system()

    def ping_ip(self, ip):
        if self.os == "Windows":
            command = "ping -n 1 "
            recv_response = "Received = 1"
        elif self.os == "Linux":
            command = "ping -c 1 "
            recv_response = "1 received"
        else:
            command = "ping -c 1 "
            recv_response = "1 received"


        response = os.popen(command + ip)
        for line in response.readlines():
            if recv_response in line:
                return True

        return False

    def __ping_threader(self, output):
        while True:
            ip = self.queue.get()
            if self.ping_ip(ip):
                self.pings.append(ip)
            if output:
                print (ip + " Live")

            self.queue.task_done()

    # finds range of ip addresses per port
    def ping_sweep(self, ip_range, output=False):
        self.pings = []
        self.queue = queue.Queue()
        local = self.network_ip.split('.')
        ip_base = local[0] + '.' + local[1] + '.' + local[2] + '.'

        for x in range(100):
            thread = threading.Thread(target=self.__ping_threader, args=(output,))
            thread.daemon = True
            thread.start()

        for ip in range(ip_range[0], ip_range[1]):
            self.queue.put(ip_base + str(ip))

        self.queue.join()

        return self.pings