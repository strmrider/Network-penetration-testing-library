import protocols.ethernet as ethernet
import protocols.ipheader as ipheader
import protocols.tcp as tcp
import protocols.udp as udp
import protocols.http as http
import time

TCP_PROTOCOL_CODE = 6
UDP_PROTOCOL_CODE = 17


class Packet:
    def __init__(self, data):
        self.scan_time = time.time()
        self.raw_data = data
        self.ethernet = ethernet.EthernetHeader(data)
        self.ip = ipheader.IpHeader(data[14:])
        self.transport = None
        self.application = None
        self.payload = self.set_payload()

    def set_transport_layer_protocol(self):
        if self.ip.protocol == TCP_PROTOCOL_CODE:
            self.transport = tcp.TCP(data[self.ip.ihl:])
        elif self.ip.protocol == UDP_PROTOCOL_CODE:
            self.transport = udp.UDP(data[self.ip.ihl:])

    def set_payload(self):
        if self.transport:
            return data[self.transport.data_offset:]
        else:
            return None

    def set_app_layer_protocol(self):
        # HTTP request
        if self.transport.src_port == 80 or self.transport.dest_port == 80:
            self.application = http.HTTP(data[self.transport.data_offset:])

    def __str__(self):
        return self.ethernet.__str__() + "\n" + self.ip.__str__() + "\n" + self.transport.__str__()

    def summary(self):
        return self.ethernet.summary() + " " + self.ip.summary() + " " + self.transport.summary()
