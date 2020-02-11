from socket import AF_INET, SOCK_DGRAM, socket, getaddrinfo
import binascii
import argparse


def parseInput():
    parser = argparse.ArgumentParser("dns client")
    parser.add_argument('-t', type=int, default=5, metavar='timeout',
                        help='(optional) timeout gives how long to wait, in seconds, before retransmitting an unanswered query')
    parser.add_argument('-r', type=int, default=3, metavar='max-retries',
                        help='(optional) max-retries is the maximum number of times to retransmit an unanswered query before termination')
    parser.add_argument('-p', type=int, default=53, metavar='port',
                        help='(optional) port is the UDP port number of the DNS server')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-mx', default=False, action='store_true', help='(optional) send a mail server query')
    group.add_argument('-ns', default=False, action='store_true', help='(optional) send a name server query')
    parser.add_argument('server', type=str, metavar='@server',
                        help='IPv4 address of a server in the format of @a.b.c.d')
    parser.add_argument('name', type=str, metavar='name', help='domain name to query for')
    parser.print_help()
    return parser.parse_args()


def printHeader(config):
    print('DnsClient sending request for {}'.format(config.name))
    print('Server: {}'.format(config.server[1:]))
    if config.mx:
        request_type = 'MX'
    elif config.ns:
        request_type = 'NS'
    else:
        request_type = 'A'
    print('Request type: {}'.format(request_type))


def startClient(config):
    udp = socket(family=AF_INET, type=SOCK_DGRAM)
    udp.settimeout(config.t)
    message = constructMsg(config.name.lower(),config)
    for i in range(config.r):
        try:
            udp.sendto(parseMsg(message), (config.server[1:], config.p))
            reply, _ = udp.recvfrom(4096)
        except:
            print("Trial {} timeout".format(i))
            if i >= config.r - 1:
                print("ERROR\tMaximum number of retries {} exceeded".format(config.r))
                exit(0)

    reply = parseReply(reply)
    ip = readIP(reply)
    print(ip)
    print(reply)
    decode_header(reply)

    udp.close()


def parseMsg(msg):
    msg = msg.replace(" ", "").replace("\n", "")
    return binascii.unhexlify(msg)


def parseReply(reply):
    reply = binascii.hexlify(reply).decode("utf-8")
    return formatHex(reply)


def readIP(reply):
    reply = reply.split()[-4:]
    output = ""
    for item in reply:
        temp = 16*hex_dex_lookup[item[0]] + hex_dex_lookup[item[1]]
        output += str(temp)+"."
    return output[:-1]

def formatHex(hex):
    octets = [hex[i:i + 2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i + 2]) for i in range(0, len(octets), 2)]
    return " ".join(pairs)

def transInt(hex,digit):
    res = 0
    for i in range(digit):
        res += hex_dex_lookup[hex[digit-1-i]]*(16**i)
    return res

def constructMsg(domain_name,config):
    output = "AA AA 01 00 00 01 00 00 00 00 00 00"
    domain_name = domain_name.split(".")
    for name in domain_name:
        size = str(hex(len(name))).split("x")[1]
        if len(size) == 1:
            size = "0" + size
        output += " " + size
        for char in name:
            output += " " + char_hex_lookup[char]
    output += " 00"
    if   config.ns:
        output += " 00 02 00 01"
    elif config.mx:
        output += " 00 0f 00 01"
    else:
        output += " 00 01 00 01"
    return output

def decode_header(reply):
    reply = reply.split()
    id = reply[0]+reply[1]
    print('id(hex) = {}'.format(id))
    rcode = int(reply[3][1])
    print('rcode(int) = {}'.format(rcode))
    if rcode == 0:
        print('No error condition')
    else:
        print('Sth is wrong')
        return

    qd_num = transInt(reply[4]+reply[5],4)
    print('number of questions: {}'.format(qd_num))
    an_num = transInt(reply[6]+reply[7],4)
    print('number of answers: {}'.format(an_num))
    ns_num = transInt(reply[8]+reply[9],4)
    print('number of authorities: {}'.format(ns_num))
    ar_num = transInt(reply[10]+reply[11],4)
    print('number of additionals: {}'.format(ar_num))
    ptr = 12
    for i in range(qd_num):
        ptr = readsection(reply,ptr)
    for i in range(an_num):
        ptr = readsection(reply,ptr)
    for i in range(ns_num):
        ptr = readsection(reply,ptr)
    for i in range(ar_num):
        ptr = readsection(reply,ptr)

def readsection(reply,ptr):
    return 0




char_hex_lookup = {
    'a': "61", 'b': "62", 'c': "63", 'd': "64", 'e': "65", 'f': "66", 'g': "67", 'h': "68",
    'i': "69", 'j': "6A", 'k': "6B", 'l': "6C", 'm': "6D", 'n': "6E", 'o': "6F", 'p': "70",
    'q': "71", 'r': "72", 's': "73", 't': "74", 'u': "75", 'v': "76", 'w': "77", 'x': "78",
    'y': "79", 'z': "7A", '0': "30", '1': "31", '2': "32", '3': "33", '4': "34",
    '5': "35", '6': "36", '7': "37", '8': "38", '9': "39"
}

hex_dex_lookup = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15
}

if __name__ == '__main__':
    config = parseInput()
    printHeader(config)
    startClient(config)
