from socket import AF_INET6, SOCK_DGRAM, socket, getaddrinfo
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
    udp = socket(family=AF_INET6, type=SOCK_DGRAM)
    udp.settimeout(config.t)
    addrTo = (config.server[1:], config.p)
    print(getaddrinfo(config.server[1:], config.p))

    #bugs with sendto
    #udp.sendto(config.name.encode(), addrTo)

    while True:
        reply, _ = udp.recvfrom(4096).decode("utf-8")
        print(reply)

    udp.close()


if __name__ == '__main__':
    config = parseInput()
    printHeader(config)
    startClient(config)
