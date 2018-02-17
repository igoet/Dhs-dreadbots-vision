#!/usr/bin/env python

ipaddress=None
if not(ipaddress):
    # TODO: change to the IP address and port on the router.
    import socket
    # 8.8.8.8, 53 when connected to the internet
    ipaddress = [(s.connect(('10.36.56.2', 22)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

print("ipaddress=%s" % ipaddress)
