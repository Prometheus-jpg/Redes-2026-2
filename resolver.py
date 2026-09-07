import socket
from dnslib import DNSRecord
from utils import parse_DNS, Cache 

def findA(answers):
	for ans in answers:
		if ans.RRtype == 'A':
			return True
	return False

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
			if findA(parsed.p_Answer):
				cache.addDom(parsed.p_Qname, d.rr)
				return bytes(d.pack())
			else:
				return

		elif parsed.p_NScount > 0: #c
			countNS = 0
			for auth in parsed.p_Authority:
				if auth.RRtype == 'NS':
					countNS += 1
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
			if countNS == 0:
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