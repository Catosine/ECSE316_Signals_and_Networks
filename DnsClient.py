import scapy
import socket
import argparse

def parseInput():
    parser = argparse.ArgumentParser("dns client")
    parser.add_argument('-t', type=int, default=5, help='(optional) timeout gives how long to wait, in seconds, before retransmitting an unanswered query')
    parser.add_argument('-r', type=int, default=3, help='(optional) max-retries is the maximum number of times to retransmit an unanswered query before depriciation')
    parser.add_argument('-p', type=int, default=53, help='(optional) port is the UDP port number of the DNS server')
    parser.add_argument('-mx', action='store_true', help='(optional) send a mail server query')
    parser.add_argument('-ns', action='store_true', help='(optional) send a name server query')
    parser.add_argument('@server', type=str, help='(REQUIRED) IPv4 address of a server in the format of a.b.c.d')
    parser.add_argument('name', type=str, help='(REQUIRED) domain name to query for')
    return parser.parse_args()

def main():
    config = parseInput()
    print(config)

if __name__ == '__main__':
    main()
