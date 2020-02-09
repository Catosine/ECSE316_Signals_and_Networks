from dns import resolver
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


def runClient(config):
    if config.mx:
        reply = resolver.query(config.name, 'MX')
        for i in reply:
            print("MX preference = {} mail exchanger {}".format(i.preference, i.exchange))
    elif config.ns:
        reply = resolver.query(config.name, 'NS')
        for i in reply.response.answer:
            for j in i.items:
                print(j.to_text())
    else:
        reply = resolver.query(config.name, 'A')
        for i in reply.response.answer:
            for j in i.items:
                print(j.address)



if __name__ == '__main__':
    config = parseInput()
    printHeader(config)
    runClient(config)
