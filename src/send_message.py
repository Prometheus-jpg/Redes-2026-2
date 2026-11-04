import packetIP
import socket

if __name__ == "__main__":
    print("Escriba la direccion IP y el puerto del router final al que quiere que llegue el mensaje")
    IP_router_final = input("Direccion IP: ")
    puerto_router_final = int(input("Puerto: "))
    mensaje = input("Escriba el mensaje a enviar: ")

    print("\nEscriba la direccion IP y el puerto a donde se enviara el paquete")
    IP_envio = input("Direccion IP: ")
    puerto_envio = int(input("Puerto: "))

    IP_router_final_splitted = IP_router_final.split(".")
    packetInBytes = bytes([
        int(IP_router_final_splitted[0]),
        int(IP_router_final_splitted[1]),
        int(IP_router_final_splitted[2]),
        int(IP_router_final_splitted[3]),
    ])
    new_packetIP = packetIP.parse_packet(packetInBytes + puerto_router_final.to_bytes(2) + mensaje.encode())

    print("\n")
    print("Enviando paquete...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packetIP.create_packet(new_packetIP), (IP_envio, puerto_envio))
    print("Paquete enviado.")