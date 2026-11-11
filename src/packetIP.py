# Direccion_IP;Puerto;TTL;mensaje (sin los ;)
# Direccion_IP: 4 bytes, a:b:c:d c/u 1 byte
# Puerto: Entero de 2 bytes


class packetIP:
    """ Representa un paquete IP  

        Attributes:
            ip_a (int): primer byte de la IP
            ip_b (int): segundo byte de la IP
            ip_c (int): tercer byte de la IP
            ip_d (int): cuarto byte de la IP
            ip (str): string de la IP de la forma a.b.c.d
            port (int): puerto
            message (bytes): mensaje en bytes
            TTL (int): Time-To-Live del paquete
    """

    def __init__(self,):
        """ Inicializa un objeto de tipo packet IP"""
        self.ip_a = 0
        self.ip_b = 0
        self.ip_c = 0
        self.ip_d = 0
        self.ip = "0.0.0.0"
        self.port = 0
        self.message = b''
        self.TTL = 0
        self.id = 0
        self.offset = 0
        self.size = 0
        self.FLAG = 0

    def parse_packet(self, IP_packet: bytes):
        """ Guarda la informacion de un paquete IP en bytes a los parametros de la clase packetIP

            Args:
                IP_packet (bytes): paquete IP en bytes
        """
        self.ip_a = IP_packet[0]
        self.ip_b = IP_packet[1]
        self.ip_c = IP_packet[2]
        self.ip_d = IP_packet[3]
        self.ip = f'{self.ip_a}.{self.ip_b}.{self.ip_c}.{self.ip_d}'
        self.port = int.from_bytes(IP_packet[4:6])
        self.TTL = IP_packet[6]
        self.id = int.from_bytes(IP_packet[7:11])
        self.offset = int.from_bytes(IP_packet[11:15])
        self.size = int.from_bytes(IP_packet[15:19])
        self.FLAG = IP_packet[19]
        self.message = IP_packet[20:]

    def create_packet(self):
        """ Crea un paquete IP en bytes con los parametros guardados en el objeto 

            Returns:
                paquete IP en bytes
        """
        IP_dir = bytes([self.ip_a, self.ip_b, self.ip_c, self.ip_d])
        headers = (IP_dir + self.port.to_bytes(2) + bytes([self.TTL]) +
                   self.id.to_bytes(4) + self.offset.to_bytes(4) + 
                   self.size.to_bytes(4) + bytes([self.FLAG]))
        return headers + self.message


def parse_packet(IP_packet: bytes):
    """ Parsea un paquete IP en bytes a la estructura packetIP

        Args:
            IP_packet (bytes): paquete IP en bytes

        Returns:
            objeto packetIP con la informacion del paquete
    """
    newPacket = packetIP()
    newPacket.parse_packet(IP_packet)
    return newPacket

def create_packet(parsed_IP_packet: packetIP):
    """ Crea un paquete IP en bytes 

        Args:
            parsed_IP_packet (packetIP): objeto packetIP con la informacion de un paquete IP

        Returns:
            paquete IP en bytes
    """
    return parsed_IP_packet.create_packet()
