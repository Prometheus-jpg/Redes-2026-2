import socketTCP
import sys

if len(sys.argv) > 1:
    address = (sys.argv[1], int(sys.argv[2]))
    archivo = sys.argv[3]

with open(archivo, 'r', encoding='utf-8') as text:
    prueba_txt = text.read()

prueba_bin = prueba_txt.encode()

# CLIENT
client_socketTCP = socketTCP.SocketTCP()
client_socketTCP.connect(address)

#Test 1
print("Test 1")
client_socketTCP.send(prueba_bin)

#Test 2
print("Test 2")
client_socketTCP.send(prueba_bin)

client_socketTCP.close()