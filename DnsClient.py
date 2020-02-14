from socket import AF_INET, SOCK_DGRAM, socket
import binascii
import argparse
import time

def parseInput():
    parser = argparse.ArgumentParser("DnsClient.py")
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

class DNSClient:
    def __init__(self, config):
        self.config = config
        self.char_hex_lookup = {
            'a': "61", 'b': "62", 'c': "63", 'd': "64", 'e': "65", 'f': "66", 'g': "67", 'h': "68",
            'i': "69", 'j': "6A", 'k': "6B", 'l': "6C", 'm': "6D", 'n': "6E", 'o': "6F", 'p': "70",
            'q': "71", 'r': "72", 's': "73", 't': "74", 'u': "75", 'v': "76", 'w': "77", 'x': "78",
            'y': "79", 'z': "7A", '0': "30", '1': "31", '2': "32", '3': "33", '4': "34",
            '5': "35", '6': "36", '7': "37", '8': "38", '9': "39"
        }

        self.hex_dex_lookup = {
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15
        }

    def __printHeader__(self):
        print('DnsClient sending request for {}'.format(self.config.name))
        print('Server: {}'.format(self.config.server[1:]))
        if self.config.mx:
            request_type = 'MX'
        elif self.config.ns:
            request_type = 'NS'
        else:
            request_type = 'A'
        print('Request type: {}'.format(request_type))


    def sendRequest(self):
        self.__printHeader__()
        udp = socket(family=AF_INET, type=SOCK_DGRAM)
        udp.settimeout(self.config.t)
        message = self.__constructMsg__()
        start = time.time()
        if self.config.server[1] != "@" or len(self.config.server.split()) != 4:
            print("ERROR\tInvalid @server IP address. Example: @8.8.8.8")
            exit(0)
        for i in range(self.config.r):
            try:
                udp.sendto(self.__parseMsg__(message), (self.config.server[1:], self.config.p))
                reply, _ = udp.recvfrom(4096)
                if reply is not None:
                    break
            except:
                print("Trial {} timeout".format(i))
                if i >= self.config.r - 1:
                    print("ERROR\tMaximum number of retries {} exceeded".format(self.config.r))
                    exit(0)
        end = time.time()
        print("Response received after {} seconds ({} retries)".format(end-start, i))
        reply = self.__parseReply__(reply)
        self.__decodeReply__(reply)

        udp.close()

    def __parseMsg__(self, msg):
        msg = msg.replace(" ", "").replace("\n", "")
        return binascii.unhexlify(msg)


    def __parseReply__(self, reply):
        reply = binascii.hexlify(reply).decode("utf-8")
        return self.__formatHex__(reply)

    def __formatHex__(self, hex):
        octets = [hex[i:i + 2] for i in range(0, len(hex), 2)]
        pairs = [" ".join(octets[i:i + 2]) for i in range(0, len(octets), 2)]
        return " ".join(pairs)

    def __constructMsg__(self):
        output = "AA AA 01 00 00 01 00 00 00 00 00 00"
        domain_name = self.config.name.lower().split(".")
        for name in domain_name:
            size = str(hex(len(name))).split("x")[1]
            if len(size) == 1:
                size = "0" + size
            output += " " + size
            for char in name:
                output += " " + self.char_hex_lookup[char]
        output += " 00"
        if self.config.ns:
            output += " 00 02 00 01"
        elif self.config.mx:
            output += " 00 0f 00 01"
        else:
            output += " 00 01 00 01"
        return output

    def __readShotcut__(self, reply, hex):
        decode = ""
        rest_idx = self.__hexToInt__(hex) & 16383
        while True:
            if reply[rest_idx] == 'c0':
                return decode+self.__readShotcut__(reply, reply[rest_idx:rest_idx+2])
            rest_len = self.__hexToInt__(reply[rest_idx:rest_idx+1])
            if rest_len == 0:
                break
            rest_idx += 1
            decode += self.__hexToStr__(reply[rest_idx:rest_idx+rest_len]) + "."
            rest_idx += rest_len
        return decode

    def __readBlock__(self, reply, ptr, num, auth):
        for i in range(num):
            while reply[ptr]!="00":
                ptr+=1
            type = " ".join(reply[ptr:ptr+2])
            ptr += 4
            ttl = self.__hexToInt__(reply[ptr:ptr+4])
            ptr += 4
            len = self.__hexToInt__(reply[ptr:ptr+2])
            ptr += 2
            ptr_cp = ptr
            if type == "00 0f":
                # mx
                pref = self.__hexToInt__(reply[ptr:ptr+2])
                ptr += 2
                alias = ""
                while True:
                    word_len = self.__hexToInt__(reply[ptr:ptr+1])
                    if word_len == 0:
                        break
                    if word_len == 192:
                        # shortcut detected
                        alias += self.__readShotcut__(reply, reply[ptr:ptr+2])
                        break

                    ptr += 1
                    alias += self.__hexToStr__(reply[ptr:ptr+word_len])+"."
                    ptr += word_len
                alias = alias[:-1]
                print("MX\t{}\t{}\t{}\t{}".format(alias, pref, ttl, auth))
            elif type == "00 02":
                # ns
                prefix = ""
                while True:
                    if reply[ptr] == "c0":
                        prefix += self.__readShotcut__(reply, reply[ptr:ptr+2])[:-1]
                        break
                    len_prefix = self.__hexToInt__(reply[ptr:ptr+1])
                    if len_prefix == 0:
                        prefix = prefix[:-1]
                        break
                    ptr+=1
                    prefix += self.__hexToStr__(reply[ptr:ptr+len_prefix])+"."
                    ptr += len_prefix
                print("NS\t{}\t{}\t{}".format(prefix, ttl, auth))
                ptr += 2
            elif type == "00 01":
                # a type
                ip = self.__hexToIP__(reply[ptr:ptr+len])
                ptr+=len
                print("IP\t{}\t{}\t{}".format(ip, ttl, auth))
            else:
                print("ERROR\tUnexpected response. Section {} QType {}".format(i, type))
                ptr+=len

            ptr = ptr_cp + len

        return ptr

    def __decodeReply__(self, reply):
        reply = reply.split()
        num_of_ans = self.__hexToInt__(reply[6:8])
        if num_of_ans > 0:
            print("***Answer Section ({} records)***".format(num_of_ans))
        else:
            print("NOTFOUND")
            return
        auth = "auth" if self.__hexToInt__(reply[2:4]) & 1024 else "nonauth"
        num_of_add = self.__hexToInt__(reply[10:12])
        ptr = 12
        while True:
            increment = self.__hexToInt__(reply[ptr])
            ptr += increment+1
            if increment == 0:
                break

        ptr += 6

        ptr = self.__readBlock__(reply, ptr, num_of_ans, auth)

        if num_of_add <= 0:
            return

        print("***Additional Section ({} records)***".format(num_of_add))
        while reply[ptr]!="00":
            ptr+=1
        ptr = self.__readBlock__(reply, ptr, num_of_add, auth)

        return

    def __hexToInt__(self, arr):
        result = 0
        idx = 0
        for item in arr[::-1]:
            for c in item[::-1]:
                result += self.hex_dex_lookup[c] * (16)**idx
                idx+=1
        return result

    def __hexToStr__(self, arr):
        decoded = ""
        for item in arr:
            decoded += chr(self.hex_dex_lookup[item[1]] + self.hex_dex_lookup[item[0]]*16)
        return decoded

    def __hexToIP__(self, arr):
        ip = ""
        for item in arr:
            ip += str(self.hex_dex_lookup[item[1]] + self.hex_dex_lookup[item[0]]*16) + "."
        return ip[:-1]

if __name__ == '__main__':
    try:
        config = parseInput()
    except:
        print("ERROR\tInvalid Input Parameters. Please type python DnsClient.py -h for helping info.")
        exit(0)
    client = DNSClient(config)
    client.sendRequest()
