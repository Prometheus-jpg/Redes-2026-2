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

def resolver(mensaje_consulta: bytes, ip_addr='198.41.0.4'):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.sendto(mensaje_consulta, (ip_addr, 53))
		data, _ = sock.recvfrom(4096)
		d = DNSRecord.parse(data)
	finally:
		sock.close()
	
	parsed = parse_DNS(d)
	while True:
		con = False
		if parsed.p_ANcount > 0: #b
			for answer in parsed.p_Answer:
				if answer.RRtype == 'A':
					return bytes(d.pack())

		elif parsed.p_NScount > 0: #c
			for auth in parsed.p_Authority:
				if auth.RRtype == 'NS':
					if parsed.p_ARcount > 0: #c.i
						for add in parsed.p_Additional:
							if add.RRtype == 'A':
								sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
								sock.sendto(mensaje_consulta, (str(add.RRdata), 53))
								data, _ = sock.recvfrom(4096)
								d = DNSRecord.parse(data)
								parsed = parse_DNS(d)
								con = True
								break
					if con:
						break
					#c.ii
					nsauth = str(auth.RRdata)
					rec = resolver(nsauth.encode())
					if rec:
						rec = DNSRecord.parse(rec)
						parsedRec = parse_DNS(rec)
						sock.sendto(bytes(d.pack()), (parsedRec.p_Answer[-1].RRdata, 53))
						data, _ = sock.recvfrom(4096)
						d = DNSRecord.parse(data)
						parsed = parse_DNS(d)
						break
					else:
						return
		else:
			return	


if __name__ == "__main__":
	socket_addres = ('10.0.2.15', 8000)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(socket_addres)

	try:
		while True:
			data, addr_client = sock.recvfrom(4096)
			res = resolver(data)
			if res:
				sock.sendto(res, addr_client)
	finally:
		sock.close()