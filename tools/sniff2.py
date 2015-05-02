#!/usr/bin/python

import sys

from scapy.all import *

pkts = sniff(offline='pcap/portroll.pcap',
             lfilter=lambda p: p.haslayer(TCP) and 
             (p.sport==53269 or p.sport==53270 or 
              p.dport==53269 or p.dport==53270))

for p in pkts:
    print p.time - pkts[0].time, p.summary(),
    if p.haslayer(Raw) and 'GET' in str(p):
        print str(p.getlayer(Raw)).split('\r')[0], p.sport
    else:
        print
