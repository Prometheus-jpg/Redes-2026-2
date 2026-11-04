# Direccion_IP;Puerto;mensaje (sin los ;)
# Direccion_IP: 4 bytes, a:b:c:d c/u 1 byte
# Puerto: Entero de 2 bytes


class packetIP:
    def __init__(self,):
        self.ip_a = 0
        self.ip_b = 0
        self.ip_c = 0
        self.ip_d = 0
        self.port = 0
        self.message = b''

    def parse_packet(self, IP_packet: bytes):
        self.ip_a = IP_packet[0]
        self.ip_b = IP_packet[1]
        self.ip_c = IP_packet[2]
        self.ip_d = IP_packet[3]
        self.port = int.from_bytes(IP_packet[4:6])
        self.message = IP_packet[6:]

    def create_packet(self):
        IP_dir = bytes([self.ip_a, self.ip_b, self.ip_c, self.ip_d])
        return IP_dir + self.port.to_bytes(2) + self.message


def parse_packet(IP_packet: bytes):
    newPacket = packetIP()
    newPacket.parse_packet(IP_packet)
    return newPacket

def create_packet(parsed_IP_packet: packetIP):
    return parsed_IP_packet.create_packet()
