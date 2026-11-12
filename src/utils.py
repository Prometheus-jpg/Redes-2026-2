from RoundRobin import RoundRobin
import packetIP
import math

def check_routes(routes_file_name: str, destination_address: tuple[str, int], roundRobin: tuple[RoundRobin, str]): 
    """ Funcion encargada de revisar la tabla de rutas e indicar el siguiente salto, si hay mas de una ruta posible
        se alternan las posibles rutas usando round-robin.

        Args:
            routes_file_name (str): archivo con la tabla de rutas
            destination_addres (tuple[str, int]): direccion IP y puerto
            roundRobin (tuple[RoundRobin, str]): objeto encargado de alternar las rutas usando round-robin

        Returns:
            Par (direccion IP, puerto) del siguiente salto o None si no se encuentra
    """
    (ip_destino, puerto_destino) = destination_address

    with open(routes_file_name, 'r', encoding='utf-8') as text:
        routes_file = text.read()
    routes = routes_file.split("\n")
    interfaces = roundRobin[0].routers[roundRobin[1]]

    for i in range(len(routes)):
        route_split = routes[i].split(" ")
        ip_cidr = route_split[0]
        puerto_inicial = int(route_split[1])
        puerto_final = int(route_split[2])
        mtu = int(route_split[5])
        if puerto_inicial <= puerto_destino <= puerto_final:
            next_hop_i = interfaces[f'{puerto_inicial}-{puerto_final}']
            next_hop_i[0] = (next_hop_i[0] + 1) % next_hop_i[1]
            interfaces[f'{puerto_inicial}-{puerto_final}'][0] = next_hop_i[0]

            next_route = routes[i + next_hop_i[0]].split(" ")
            (next_hop_IP, next_hop_puerto) = (str(next_route[3]), int(next_route[4]))
            return (next_hop_IP, next_hop_puerto), mtu
    
    return None


def fragment_IP_packet(IP_packet: bytes, MTU: int):
    parsed = packetIP.parse_packet(IP_packet)
    res: list[bytes] = []

    size_packet = len(IP_packet)
    if size_packet <= MTU:
        res.append(IP_packet)
    else:
        message_og = parsed.message
        initial_offset = parsed.offset
        total_size = parsed.size
        MTU_message = MTU - 20 # tamaño headers = 20 Bytes
        n_fragment = math.ceil(total_size / MTU_message) # numero de fragmentos
        for i in range(n_fragment):
            lo = i * MTU_message
            hi = lo + MTU_message
            parsed.message = message_og[lo:hi]
            parsed.size = len(parsed.message)
            parsed.offset = initial_offset + lo
            parsed.FLAG = 1 if i < n_fragment-1 else 0 # FLAG=0 si es el ultimo fragmento
            res.append(packetIP.create_packet(parsed))
        
    return res


def reassemble_IP_packet(fragment_list: list[bytes]):
    if len(fragment_list) == 1:
        parsed = packetIP.parse_packet(fragment_list[0])
        if parsed.offset == 0 and parsed.FLAG == 0:
            return fragment_list[0]
        else: 
            return None

    fragment = [packetIP.parse_packet(frag) for frag in fragment_list]
    fragment.sort(key=lambda x: x.offset)

    message = b''
    last_offset, last_size = 0, 0
    for i in range(len(fragment)):
        if ((i == len(fragment)-1 and fragment[i].FLAG != 0) or 
            fragment[i].offset > last_offset + last_size):
            return None
        else:
            message += fragment[i].message
            last_offset = fragment[i].offset
            last_size = fragment[i].size

    fragment[-1].offset = 0
    fragment[-1].size = len(message)
    fragment[-1].message = message
    return packetIP.create_packet(fragment[-1])