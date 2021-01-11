import requests, socket

methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TEST', 'TRACE']
headers = ['Server', 'Date', 'Via', 'X-Powered-By', 'X-Country-Code', 'Connection', 'Content-Length']

class SecurityHeaders:
    def __init__(self):
        self.headers = {'Strict-Transport-Security': -1,
                    'Content-Security-Policy': -1,
                   'X-Content-Type-Options': 'nosniff',
                   'X-Frame-Options': 'deny',
                   'X-Permitted-Cross-Domain-Policies': 'none',
                   'X-XSS-Protection': '1; mode = block',
                    'Public-Key-Pins': -1
                    }

    def __getitem__(self, item):
        return self.headers[item]

def fix_url(url:str):
    if url.find('https://') != -1:
        return url
    else:
        return "http://" + url

NO_DETAILS = 'No details'


def check_http_methods(url):
    url = fix_url(url)
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


def check_http_headers(url):
    url = fix_url(url)
    request = requests.get(url)
    responses = []
    for header in headers:
        try:
            result = request.headers[header]
            responses.append((header, result))
        except Exception:
            responses.append((header, NO_DETAILS))

    return responses

def check_http_security_headers(url, security_headers):
    url = fix_url(url)
    responses = []
    req = requests.get(url.strip())
    security_headers = SecurityHeaders() if not security_headers else security_headers
    headers = security_headers.headers.keys()
    for header in headers:
        try:
            res = req.headers[header]
            expected_value = security_headers[header]
            if expected_value != -1 and res == expected_value:
                responses.append((header, True))
            else:
                responses.append((header, res))
        except:
            responses.append((header, 'Not set'))

    return responses

def grab_banner(url:str, port):
    url = url.replace('http://', '').replace('https://', '').replace('www.', '')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = socket.gethostbyname(url)
    s.connect((ip,port))
    try:
        s.send(b'GET HTTP/1.1 \r\n')
        ret = s.recv(1024)
        return str(ret)
    except Exception as e:
        return NO_DETAILS
