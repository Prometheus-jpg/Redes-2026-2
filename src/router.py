import sys
import socket
import packetIP
from check_routes import check_routes
from RoundRobin import RoundRobin
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ruta = BASE_DIR 

if len(sys.argv) < 4:
    print("Se debe pasar el IP, puerto y archivo con las rutas del router como argumentos.")
    sys.exit(1)
else:
    router_IP = sys.argv[1]
    router_puerto = sys.argv[2]
    router_rutas_path = ruta / "routes_files" / sys.argv[3]

if __name__ == "__main__":
    router_address = (router_IP, int(router_puerto))

    router_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    router_sock.bind(router_address)

    roundRobin = RoundRobin()
    router_name = roundRobin.add_router_zones(str(router_rutas_path))

    while True:
        try:
            data, _ = router_sock.recvfrom(4096)
            parsed = packetIP.parse_packet(data)
            if parsed.TTL == 0:
                print(f'Se recibió paquete {parsed.ip};{parsed.port};{parsed.TTL};{parsed.message} con TTL 0')
                continue
            if parsed.ip == router_address[0] and parsed.port == router_address[1]:
                print(parsed.message.decode())
            else:
                next_hop = check_routes(str(router_rutas_path), (parsed.ip, parsed.port), (roundRobin, router_name))
                if not next_hop:
                    print(f"No hay rutas hacia ({parsed.ip}, {parsed.port}) para paquete {parsed.ip};{parsed.port};{parsed.TTL};{parsed.message}")
                else:
                    parsed.TTL -= 1
                    redirigir_mensaje = f"redirigiendo paquete {parsed.ip};{parsed.port};{parsed.TTL};{parsed.message} con destino final " \
                                        f"({parsed.ip}, {parsed.port}) desde ({router_IP}, {router_puerto}) hacia ({next_hop[0]}, {next_hop[1]})"
                    print(redirigir_mensaje)
                    router_sock.sendto(packetIP.create_packet(parsed), next_hop)
        except:
            continue
