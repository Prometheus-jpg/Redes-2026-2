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

class Slot:
	def __init__(self, domName, repeticiones, ip):
		self.domName 	  = domName
		self.repeticiones = repeticiones
		self.ip 		  = ip

class Cache:
	slots = [Slot('', 0, ''), Slot('', 0, ''), Slot('', 0, '')]
	last20 = []

	def findDom(self, dom_name):
		for slot in self.slots:
			if slot.domName == dom_name:
				slot.repeticiones += 1
				return slot.ip
		return -1

	def findInLast(self, dom_name):
		for i in range(len(self.last20)-1):
			if self.last20[i].domName == dom_name:
				return i
		return -1

	def indexMin(self, list):
		index = 0
		for i in range(1, len(list)-1):
			if list[i].repeticiones <= list[index].repeticiones:
				index = i
		return index
	
	def indexMax(self, list):
		index = 0
		for i in range(1, len(list)-1):
			if list[i].repeticiones >= list[index].repeticiones:
				index = i
		return index
	
	def updateCache(self):
		while len(self.last20) > 0:
			index_max = self.indexMax(self.last20)
			index_min = self.indexMin(self.slots)
			max_last20 = self.last20[index_max]
			min_slots = self.slots[index_min]
			if max_last20.repeticiones >= min_slots.repeticiones:
				self.slots[index_min] = max_last20
				self.last20.pop(index_max)
			else:
				break

	def addDom(self, dom_name, new_ip):
		dom_in_last = self.findInLast(dom_name)
		if dom_in_last != -1:
			self.last20[dom_in_last].repeticiones += 1
		elif len(self.last20) < 20:
			self.last20.append(Slot(dom_name, 1, new_ip)) 
		else:
			index_min = self.indexMin(self.last20)
			self.slots[index_min].domName 	   = dom_name
			self.slots[index_min].repeticiones = 1
			self.slots[index_min].ip 		   = new_ip
		self.updateCache()


def resolver(mensaje_consulta: bytes, ip_addr='198.41.0.4'):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.sendto(mensaje_consulta, (ip_addr, 53))
		data, _ = sock.recvfrom(4096)
		d = DNSRecord.parse(data)
	finally:
		sock.close()
	cache = Cache()
	parsed = parse_DNS(d)
	dom_cache = cache.findDom(parsed.p_Qname)
	if dom_cache != -1:
		print(f"(debug) Uso de direccion IP en cache de dominio {parsed.p_Qname}")
		a = DNSRecord.parse(mensaje_consulta)
		for ans in dom_cache:
			a.add_answer(ans)
		return bytes(a.pack())
	while True:
		con = False
		if parsed.p_ANcount > 0: #b
			for answer in parsed.p_Answer:
				if answer.RRtype == 'A':
					cache.addDom(parsed.p_Qname, d.rr)
					return bytes(d.pack())

		elif parsed.p_NScount > 0: #c
			for auth in parsed.p_Authority:
				if auth.RRtype == 'NS':
					if parsed.p_ARcount > 0: #c.i
						for add in parsed.p_Additional:
							if add.RRtype == 'A':
								print(f"(debug) Consultando '{parsed.p_Qname}' a '{auth.RRdata}' con direccion IP '{add.RRdata}'")
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
					nsauth = DNSRecord.question(str(auth.RRdata))
					rec = resolver(bytes(nsauth.pack()))
					if rec:
						rec = DNSRecord.parse(rec)
						parsedRec = parse_DNS(rec)
						print(f"(debug) Consultando '{parsed.p_Qname}' a '{auth.RRdata}' con direccion IP '{parsedRec.p_Answer[-1].RRdata}'")
						sock.sendto(mensaje_consulta, (str(parsedRec.p_Answer[-1].RRdata), 53))
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