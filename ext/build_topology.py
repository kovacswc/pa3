import os
import sys
import random
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
sys.path.append("../../")

from mininet.log import setLogLevel, info
from subprocess import Popen
from time import sleep, time

import signal

class TestTopo(Topo):

    def build(self):

        soleSwitch = self.addSwitch("s1")
        attacker = self.addHost("h1", ip='NULL')
        victim = self.addHost("h2", ip='NULL')
        bystander = self.addHost("h3", ip='NULL')

        self.addLink(soleSwitch, victim, delay = "5ms")
        self.addLink(soleSwitch, attacker, delay = "5ms")
        self.addLink(soleSwitch, bystander)

class DHCPTopo(Topo):
    def build(self):

        soleSwitch = self.addSwitch("s1")
        attacker = self.addHost("h1", ip='NULL')
        victim = self.addHost("h2", ip='NULL')
        bystander = self.addHost("h3", ip='NULL')
        dhcpServer = self.addHost("h4")
        
        self.addLink(soleSwitch, victim, delay = "5ms")
        self.addLink(soleSwitch, attacker, delay = "5ms")
        self.addLink(soleSwitch, bystander)
        self.addLink(soleSwitch, dhcpServer)
        
def startDHCP( host):
    hInt = host.defaultIntf()
    host.cmd('dhclient -v -d -r', hInt)
    host.cmd('dhclient -v -d 1> /tmp/dhclient.log 2>&1', hInt, '&')

def waitForIp(host):
    info('*', host, 'waiting for IP')
    while True:
        host.defaultIntf().updateIP()
        if host.IP():
            break
        info('.')
        sleep(1)
    info ('\n')
    info('*', host, 'is now usign', host.cmd('grep nameserver /etc/resolv.conf'))
    info(host, 'is now using IP', host.IP(), '\n')
        
def getVicIp(atk,vic):
    vicIp = vic.IP()
    atkMac = atk.MAC()


    
    print "The attaker MAC is " + str(atk.MAC())
    print "The vic's IP is " + str(vic.IP())
    print "The interface is " + str(atk.defaultIntf())

    atkOut = atk.cmd('python create_dhcp.py', atkMac, vicIp)

    print "THE OUTPUT OF TRYING TO STEAL DHCP IS: "

    print atkOut
    splitOut = atkOut.split('\n')


    #Make it easier to use it in mininet, abstracting away
    #how an attacker can set his own IP/MAC
    atk.setIP(splitOut[-3])
    atk.defaultIntf().setMAC(splitOut[-2])
    print atk.IP()
    print atk.MAC()

def tryRelease(atk, vic):
    vicIp = vic.IP()
    vicMac = vic.MAC()
    relOut = atk.cmd('python release_dhcp.py', vicIp, vicMac)
    print relOut
    
def experiment(net, testNum):
    net.start()

    if testNum == 3:
        dhcpServer = net.get('h4')
        #Don't forget to remind people to run "sudo apt install udhcpd"
        print dhcpServer.cmd('udhcpd')
        return
    
    atk, vic, bystand = net.get('h1', 'h2', 'h3')
    info(atk, 'initial ip is ', atk.IP(), '\n')
    startDHCP(atk)
    waitForIp(atk)

    startDHCP(vic)

    waitForIp(vic)

    startDHCP(bystand)
    waitForIp(bystand)

    info("Atk attempting to break Vic's IP-MAC binding\n")
    tryRelease(atk, vic)

    sleep(1)
    
    getVicIp(atk, vic)

    #Some slight delay needed, otherwise thinks its the old IP?
    sleep(3)

    print "Before pinging, the bystander sees:"
    
    #h1 is unable to ping h2
    bystand.cmd("ping -c1 " + str(atk.IP()))
    print bystand.cmd("arp")
    
    net.pingAll()
    print "After one set of pings: "
    print bystand.cmd("arp")
    sleep(5)
    net.pingAll()

    print "The victim's MAC is " + str(vic.MAC()) + " IP is " + str(vic.IP())
    print "The attacker's MAC is " + str(atk.MAC())
    print " and advertising IP as " + str(atk.IP())
    print "The bystander believes " + str(vic.IP()) + " is at "
    print bystand.cmd("arp")
    
    net.stop()

def main():
    test = 1
    if len(sys.argv) > 1:
        test = int(sys.argv[1])

    topo = TestTopo()
    pox_arguments = []
    if test == 1:
        pox_arguments = ['../../pox.py', 'forwarding.l2_learning',
                         'proto.dhcpd','--count=4']
    if test == 2:
        pox_arguments = ['../../pox.py', 'forwarding.l2_learning', 'proto.dhcpd',
                         '--count=4',"ext.arp_resp_dhcp" ]       

    if test == 3:
        topo = DHCPTopo()
        pox_arguments = ['../../pox.py', 'forwarding.l2_learning',
                         'proto.dhcpd','--count=4']
    with open(os.devnull, "w") as fnull:
        pox_process = Popen(pox_arguments, stdout=fnull,
                            stderr=fnull, shell=False, close_fds=True)

    sleep(1)
    net = Mininet(topo = topo, host=CPULimitedHost, link = TCLink, controller=RemoteController)
    net.addController('pox', RemoteController, ip = '127.0.0.1', port = 6633)
    experiment(net, test)
    pox_process.send_signal(signal.SIGINT)
    pox_process.kill()
    
if __name__ == "__main__":
    setLogLevel('info')
    main()
