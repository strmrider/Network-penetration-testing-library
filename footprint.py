import requests
import socket

methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TEST', 'TRACE']
headers = ['Server', 'Date', 'Via', 'X-Powered-By', 'X-Country-Code', 'Connection', 'Content-Length']

NO_DETAILS = 'No details'


def check_http_methods(url):
    responses = []
    for method in methods:
        req = requests.request(method, url)
        if method == "TRACE":
            if 'TRACE / HTTP/1.1' in req.text:
                responses.append(('TRACE', 'Cross Site Tracing(XST) is possible'))
            else:
                responses.append(('TRACE', req.status_code, req.reason))
        else:
            responses.append((method, req.status_code, req.reason))

    return responses


def check_http_header(url):
    request = requests.get(url)
    responses = []
    for header in headers:
        try:
            result = request.headers[header]
            responses.append((header, result))
        except Exception:
            responses.append((header, NO_DETAILS))

    return responses


def grab_banner(url, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    s.connect((url,port))
    try:
        s.send('GET HTTP/1.1 \r\n')
        ret = s.recv(1024)
        return str(ret)
    except Exception:
        return NO_DETAILS
