import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE

class resouceRecord:
	def __init__(self, RRname, RRtype, RRclass, RRttl, RRdata):
		self.RRname  = RRname
		self.RRtype  = RRtype
		self.RRclass = RRclass
		self.RRttl   = RRttl
		self.RRdata  = RRdata

class DNSparsed:
	def __init__(self, p_Qname, p_ANcount, p_NScount, p_ARcount, p_Answer, p_Authority, p_Additional):
		self.p_Qname 	  = p_Qname
		self.p_ANcount    = p_ANcount
		self.p_NScount 	  = p_NScount
		self.p_ARcount 	  = p_ARcount
		self.p_Answer 	  = p_Answer
		self.p_Authority  = p_Authority
		self.p_Additional = p_Additional

def parse_DNS(dnslib_message):
	Qname   = dnslib_message.get_q().get_qname()
	ancount = dnslib_message.header.a
	nscount = dnslib_message.header.auth
	arcount = dnslib_message.header.ar

	answers = []
	if ancount > 0:
		for a in dnslib_message.rr:
			answer = resouceRecord(a.get_rname(), QTYPE.get(a.rtype), CLASS.get(a.rclass), a.ttl, a.rdata)
			answers.append(answer)

	auths = []
	if nscount > 0:
		for a in dnslib_message.auth:
			auth = resouceRecord(a.get_rname(), QTYPE.get(a.rtype), CLASS.get(a.rclass), a.ttl, a.rdata)
			auths.append(auth)

	additionals = []
	if arcount > 0:
		for a in dnslib_message.ar:
			additional = resouceRecord(a.get_rname(), QTYPE.get(a.rtype), CLASS.get(a.rclass), a.ttl, a.rdata)
			additionals.append(additional)

	return DNSparsed(Qname, ancount, nscount, arcount, answers, auths, additionals)


if __name__ == "__main__":
	socket_addres = ('10.0.2.15', 8000)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(socket_addres)

	try:
		while True:
			data, _ = sock.recvfrom(1024)
			d = DNSRecord.parse(data)
			parsed = parse_DNS(d)
	finally:
		sock.close()