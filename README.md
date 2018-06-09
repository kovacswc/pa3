# pa3

Note: These were tested on an Ubuntu 18.04 VM on Google Compute.

To set up and run the experiments:

Dependencies: scapy (pip install scapy), udhcpd

1) Install Mininet
2) Copy the ext folder into pox/pox/ directory (and not into the pox/ext directory)
3) There are two scenarios that can be run:
  a) sudo python build_topology.py 2
  b) sudo python build_topology.py 3

a) is using the DHCP server provided by POX and b) is using udhcpd as an external DHCP server

Give it a few minutes to run. If the script completes, know that the attacker was able to get the victim's IP (designed to hang otherwise). The pingAll output should demonstrate whether or not the victim (h2) is blackholed.

PingAll key:
h1 = Attacker
h2 = Victim
h3 = Bystander
h4 (if present) = external DHCP server

The ARP cache of the bystander is also printed to show that the IP that was bound to the victim now corresponds to a random MAC in the test 2 variant. In the test 3 variant, this will actually correspond to the victim's MAC as DHCP routing implemented is simply only based on IP, so won't route ARPs. It still blackholes the victim because the MAC is irrelevant and the route to the attacker based on the IP is already set up.

Notes:
-- If the external server variant is run too much, then it may hang as all the leases have been given away (one lease is given away each run, unreleased as its bound to arandom MAC)
-- If interested, can view the series of DHCP requests by starting up the controller in a different terminal and running the test:

For build_topology.py 2, the corresponding controller code to run is:
../../pox.py forwarding.l2_learning proto.dhcpd --count=4 ext.arp_resp_dhcp

For build_topology.py 3:
../../pox.py ext.l2_sniff_dhcp