import struct
import socket


class IpV4Flags:
    def __init__(self, flags):
        self.reserved = 0
        # no fragment flag
        self.nf = flags >> 1
        # more fragment flag
        self.dm = flags & 0x1


# receives data from 14 [14:]
class IpHeader:
    def __init__(self, data):
        header = struct.unpack('! 2B 3H 2B H 4s 4s', data[:20])
        self.version = header[0] >> 4
        # internet Header Length
        self.ihl = (header[0] & 15) * 4
        # type of service
        self.toc = header[1] >> 2
        self.total_length = header[2]
        # identification
        self.id = header[3]
        self.flags = IpV4Flags(header[4] >> 13)
        # fragment offset
        self.offset = header[4] & 0x1fff
        # time to live
        self.ttl = header[5]
        self.protocol = header[6]
        self.checksum = header[7]
        self.source_ip = socket.inet_ntoa(header[8])
        self.destination_ip = socket.inet_ntoa(header[9])

    def __str__(self):
        return "IP Header\n" \
               "===========\n"\
                "Version: {}\n"\
                "IHL: {}\n"\
                "TOC: {}\n" \
                "total length: {}\n" \
                "Identification: {}\n" \
                "Time to Live: {}\n" \
                "Protocol: {}\n" \
                "checksum: {}\n" \
                "source_ip: {}\n" \
                "destination_ip: {}\n".format(self.version, self.ihl, self.toc, self.total_length, self.id, self.ttl,
                                            self.protocol, self.checksum, self.source_ip, self.destination_ip)

    def summary(self):
        return "Version: {} TTL: {} Protocol: {} source IP: {} Destination IP: {}".format(self.version, self.ttl,
                                                                                          self.protocol,
                                                                                          self.source_ip,
                                                                                          self.destination_ip)

