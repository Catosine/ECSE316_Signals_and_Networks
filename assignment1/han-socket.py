# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 21:20:50 2020

@author: zhouh
"""

# This is the file for DNS client
import socket
import sys  
import argparse
import time

print("\n=====DNSClient starts running!=====\n")

#check input
print('Checking input...')
parser = argparse.ArgumentParser()
parser.add_argument('-t', dest = 'timeout', type = float, default = 5.0, help='timeout')
parser.add_argument('-r', dest = 'retries', type = int, default = 3, help='max-retries')
parser.add_argument('-p', dest = 'port', type = int, default = 53, help='port')
group = parser.add_mutually_exclusive_group()
group.add_argument("-mx", default= False, action="store_true", help= 'Mail server')
group.add_argument("-ns", default= False, action="store_true", help= 'Name server')
parser.add_argument('server', type = str, help = 'v4IP address')
parser.add_argument('name', type = str, help = 'domain name')

parser.print_help()
args = parser.parse_args()
print('Input check complete! The input params are:')
print(args)

#connect to server
try: 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(args.timeout)
    print("Socket successfully created")
except socket.error as err: 
    print("socket creation failed with error %s" %(err))
  

  
try: 
    #host_ip = socket.gethostbyname(args.name)
    host_ip = args.server[1:]
    print("Host ip created %s"%(host_ip))
except socket.gaierror: 
  
    # this means could not resolve the host 
    print("there was an error resolving the host")
    sys.exit() 
  
# connecting to the server 
print('Trying to connect...')
suc = False
for i in range(args.retries):
    try:
        s.connect((host_ip, args.port))
        print("the socket has successfully connected to web on port == %s" %(host_ip) )
        suc = True
        break
    except socket.error as err:
        print ("Fail to connect at %1d th time."%(i+1))
        time.sleep(1)
if (suc==False):
    print("connection failed")
  




print("\n=====DNSClient running completed!=====\n")