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
    parser.add_argument('-mx', action='store_true', help='(optional) send a mail server query')
    parser.add_argument('-ns', action='store_true', help='(optional) send a name server query')
    parser.add_argument('server', type=str, metavar='@server',
                        help='IPv4 address of a server in the format of @a.b.c.d')
    parser.add_argument('name', type=str, metavar='name', help='domain name to query for')
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
    message = construct_msg(config.name)
    udp.sendto(parseMsg(message), (config.server[1:], config.p))
    reply, _ = udp.recvfrom(4096)
    print_reply(reply)

    udp.close()

def parseMsg(msg):
    msg = msg.replace(" ", "").replace("\n", "")
    return binascii.unhexlify(msg)

def print_reply(reply):
    reply = binascii.hexlify(reply).decode("utf-8")
    print(format_hex(reply))

def format_hex(hex):
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)

def construct_msg(domain_name):
    output="AA AA 01 00 00 01 00 00 00 00 00 00"
    domain_name=domain_name.split(".")
    name=domain_name[0]
    size=str(hex(len(name))).split("x")[1]
    if len(size)==1:
        size = "0"+size
    output+=" "+size
    for char in name:
        output+=" "+char_hex_lookup[char]
    name=domain_name[1]
    size=str(hex(len(name))).split("x")[1]
    if len(size)==1:
        size = "0"+size
    output+=" "+size
    for char in name:
        output+=" "+char_hex_lookup[char]
    output+=" 00 00 01 00 01"
    return output

char_hex_lookup = {
    'a': "61", 'b': "62", 'c': "63", 'd': "64", 'e': "65", 'f': "66", 'g': "67", 'h': "68",
    'i': "69", 'j': "6A", 'k': "6B", 'l': "6C", 'm': "6D", 'n': "6E", 'o': "6F", 'p': "70",
    'q': "71", 'r': "72", 's': "73", 't': "74", 'u': "75", 'v': "76", 'w': "77", 'x': "78",
    'y': "79", 'z': "7A"
}

if __name__ == '__main__':
    config = parseInput()
    printHeader(config)
    startClient(config)
