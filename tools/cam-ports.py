#!/usr/bin/python
#
#
#

from scapy.all import *

pkts = sniff(offline='pcap/camera.pcap')

ports = []
for p in pkts:
    if not (p.dport in ports) and p.dport != 80:
        ports.append(p.dport)

print 'ports:', ports

for port in ports:
    stream = filter(lambda p: (p.dport == port or p.sport == port) and p.haslayer(Raw), pkts)
    text = ''
    for p in stream:
        text += str(p.getlayer(Raw))

    f = open('stream.%d' % port, 'a+')
    f.write(text)
    f.close()
                                 
        
