from mimetools import Message
from StringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler


class HTTP():
    def __init__(self, data):
        request_line, http_header= request_text.split('\r\n', 1)
        headers = Message(StringIO(http_header))

    def get_header(self, header_name):
        return self.headers[header_name]