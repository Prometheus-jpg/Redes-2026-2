import sys
import socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ruta = BASE_DIR 

if len(sys.argv) < 4:
    print("Se debe pasar los headers e IP y puerto del router inicial como argumentos.")
    sys.exit(1)
else:
    headers = sys.argv[1]
    router_IP = sys.argv[2]
    router_puerto = sys.argv[3]

if __name__ == "__main__":
    router_inicial = (router_IP, int(router_puerto))

    with open(ruta / "archivo_prueba.txt", 'r', encoding='utf-8') as text:
        file = text.read()
    lines = file.split("\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    headers_campos = headers.split(";")
    ip_split = headers_campos[0].split(".")
    ip_bytes = bytes([
        int(ip_split[0]),
        int(ip_split[1]),
        int(ip_split[2]),
        int(ip_split[3]),
    ])
    headersInBytes = ip_bytes + int(headers_campos[1]).to_bytes(2) + bytes([int(headers_campos[2])])

    for line in lines:
        print(f"Enviando linea: {line}")
        sock.sendto(headersInBytes + line.encode(), router_inicial)
    sock.close()