import sys
import socket

if len(sys.argv) < 4:
    print("Se debe pasar el IP, puerto y archivo con las rutas del router como argumentos.")
    sys.exit(1)
else:
    router_IP = sys.argv[1]
    router_puerto = sys.argv[2]
    router_rutas_path = sys.argv[3]

if __name__ == "__main__":
    router_address = (router_IP, int(router_puerto))

    router_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    router_sock.bind(router_address)

    try:
        while True:
            data, _ = router_sock.recvfrom(4096)
    finally:
        router_sock.close()
