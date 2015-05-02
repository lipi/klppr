#!/usr/bin/python
#
# Print summary of HTTP requests to/from host.
# Optionally save packets to file
#
# Usage: ./sniff.py <hostname> [filename]
# Example: sudo tools/sniff.py 192.168.3.106 x.pcap

from scapy.all import *

def filter_addr(pkt):
    '''Filter HTTP packets to and from host'''
    return (pkt.haslayer(TCP) and
            (pkt.getlayer(IP).src == address or
             pkt.getlayer(IP).dst == address) and
            pkt.haslayer(Raw) and
            ('HTTP' in str(pkt.getlayer(Raw))))

def filter_mjpeg(pkt):
    return (pkt.haslayer(Raw) and 'mjpeg' in str(pkt.getlayer(Raw)))

def print_raw(pkt):
    ''''Print timestamp, ports and URI'''
    payload = str(pkt.getlayer(Raw))
    verb,uri = payload.split(' ')[:2]
    print '{:.3f} {:5} {:5} {} {}'.format(
        pkt.time, pkt.sport, pkt.dport, verb, uri)

if __name__ == '__main__':

    address = sys.argv[1]

    try:
        pkts = sniff(lfilter = filter_addr, prn = lambda p:print_raw(p))
    except Exception as e:
        print e

    if len(sys.argv) > 2:
        wrpcap(sys.argv[2], pkts)
