import socketTCP

# SERVER
server_socketTCP = socketTCP.SocketTCP()
server_socketTCP.bind(('localhost', 8000))
connection_socketTCP, new_address = server_socketTCP.accept()

with open("prueba.txt", 'r', encoding='utf-8') as text:
    prueba_txt = text.read()

prueba_bin = prueba_txt.encode()

#Test 1
print("Test 1")
buff_size = 700
full_message = connection_socketTCP.recv(buff_size)
if full_message == prueba_bin: print("Test 1: Passed")
else: print("Test 1: Failed")

#Test 2
print("Test 2")
buff_size = 200
message_part_1 = connection_socketTCP.recv(buff_size)
message_part_2 = connection_socketTCP.recv(buff_size)
message_part_3 = connection_socketTCP.recv(buff_size)
full_message = message_part_1 + message_part_2 + message_part_3
if full_message == prueba_bin: print("Test 2: Passed")
else: print("Test 2: Failed")

connection_socketTCP.recv_close()