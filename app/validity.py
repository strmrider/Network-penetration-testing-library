def check_ip_address(address):
    sections = address.split('.')
    if len(sections) != 4:
        return False
    for section in sections:
        try:
            num = int(section)
            if 0 > num > 255:
                return False
        except:
            return False

    return True

def check_mac_address(mac):
    mac = mac.replace('-', ':')
    sections = mac.split(':')
    if len(sections) == 8:
        for section in sections:
            try:
                int(section, 16)
            except:
                return False
        return True
    else:
        return False

def check_number(minimum, maximum, number):
    try:
        number = int(number)
        if minimum <= number >= maximum:
            return True
    except:
        return False
