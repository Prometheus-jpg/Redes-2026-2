import socket
import random
import time

class SocketTCP:
    def __init__(self):
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer  = 7 + 16 
        self.origen  = ('', 0)
        self.destino = ('', 0)
        self.seq     = 0
        self.v_recv  = 0
        self.len_rem = 0
        self.seq_aux = 0
        self.buff_rem = 0


    @staticmethod
    def parse_segment(TCP_msg):
        parse = dict()

        parse["seq"] = int.from_bytes(TCP_msg[:4])
        parse["SYN"] = TCP_msg[4]
        parse["ACK"] = TCP_msg[5]
        parse["FIN"] = TCP_msg[6]
        parse["data"] = TCP_msg[7:] if len(TCP_msg) > 7 else b''

        return parse

    @staticmethod
    def create_segment(parsed_TCP):
        return (parsed_TCP["seq"].to_bytes(4) + bytes([parsed_TCP["SYN"]]) + 
                bytes([parsed_TCP["ACK"]]) + bytes([parsed_TCP["FIN"]]) + 
                parsed_TCP["data"])

    def bind(self, address):
        self.origen = address
        self.socket.bind(address)

    def connect(self, address):
        self.socket.settimeout(0.3)
        self.seq = random.randint(0, 100)
        syn_ack_fin = bytes([1,0,0]) 
        self.bind(('localhost', 0))
        while True:
            try:
                self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, address)
                res, _ = self.socket.recvfrom(self.buffer)
                parse = self.parse_segment(res)
                if parse["SYN"] == 1 and parse["ACK"] != 0 and parse["seq"] == self.seq+1:
                    self.seq = parse["seq"] + 1
                    syn_ack_fin = bytes([0,parse["ACK"],0])
                    self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, address)
                    self.destino = address
                    return
            except: 
                print(f"(debug): connect - timeout terminado enviando SYN con seq {self.seq}")
                continue

    def accept(self):
        while True:
            res, res_address = self.socket.recvfrom(self.buffer)
            parse = self.parse_segment(res)
            if parse["SYN"] != 0:
                self.seq = parse["seq"] + 1
                syn_ack_fin = bytes([parse["SYN"],1,0])
                self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, res_address)
                new_sock = SocketTCP()
                new_sock.socket  = self.socket
                new_sock.origen  = self.origen
                new_sock.seq     = self.seq
                new_sock.destino = res_address
                return new_sock, res_address

    def send(self, message):
        self.socket.settimeout(0.3)
        syn_ack_fin = bytes([0,0,0])
        lenght_message = len(message)
        segment = lenght_message.to_bytes(4)
        while True:
            self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin+segment, self.destino)
            try:
                res_length, _ = self.socket.recvfrom(self.buffer)
                parsed = self.parse_segment(res_length)
                if parsed["ACK"] == 1 and parsed["seq"] == self.seq+len(segment):
                    self.seq = parsed["seq"]
                    break
            except:
                print(f"(debug): send - timeout terminado enviando largo de mensaje con seq {self.seq}")
                continue
        i = 0
        while i < lenght_message:
            segment = message[i:i+16]
            self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin+segment, self.destino)
            try:
                res, _ = self.socket.recvfrom(self.buffer)
                parsed = self.parse_segment(res)
                if parsed["ACK"] == 1 and parsed["seq"] == self.seq+len(segment):
                    self.seq = parsed["seq"]
                    i += 16
            except:
                print(f"(debug): send - timeout terminado enviando segmento con seq {self.seq}")
                continue

    def recv(self, buff_size):
        message_received = b""
        message_length = 0 if self.v_recv==0 else self.len_rem
        while (len(message_received) - min(message_length, buff_size)) < 0 or self.v_recv == 0:
            data, _ = self.socket.recvfrom(self.buffer)
            parsed = self.parse_segment(data)
            if parsed["SYN"] == 1:
                print(f"(debug): recv - recibe SYN de nuevo con seq {parsed["seq"]}")
                parsed["ACK"] = 1
                parsed["seq"] += 1
                self.socket.sendto(self.create_segment(parsed), self.destino)
            elif parsed["seq"] < self.seq and self.seq_aux < parsed["seq"]: #segmento duplicado
                print(f"(debug): recv - segmento duplicado con seq {parsed["seq"]}")
                syn_ack_fin = bytes([0,1,0])
                self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, self.destino)
            else:
                if parsed["ACK"] == 1:
                    self.seq = parsed["seq"]
                    continue
                elif self.v_recv == 0:
                    self.seq = parsed["seq"]+len(parsed["data"])
                    message_length = int.from_bytes(parsed["data"])
                    self.v_recv = 1
                elif self.v_recv == 2:
                    self.seq += min((16-self.buff_rem), len(parsed["data"]))
                    message_received += parsed["data"][self.buff_rem:]
                    self.buff_rem = 0
                    self.seq_aux = 0
                    self.v_recv = 1
                elif buff_size-len(message_received) < 16 and message_length>buff_size:
                    max_lec = buff_size - len(message_received)
                    self.seq = parsed["seq"] + max_lec
                    self.seq_aux = self.seq
                    message_received += parsed["data"][0:max_lec]
                    self.buff_rem = max_lec
                else:
                    self.seq = parsed["seq"]+len(parsed["data"])
                    message_received += parsed["data"]

                parsed["ACK"] = 1
                parsed["seq"] = self.seq
                self.socket.sendto(self.create_segment(parsed), self.destino)
            
        if len(message_received) < message_length:
            self.v_recv = 2
            self.len_rem = message_length-len(message_received)
        if self.v_recv == 1: 
            self.v_recv = 0

        return message_received

    def close(self):
        self.socket.settimeout(0.3)
        reenv_fin = 1
        while True:
            try:
                syn_ack_fin = bytes([0,0,1])
                self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, self.destino)
                res, _ = self.socket.recvfrom(self.buffer)
                parsed = self.parse_segment(res)
                if parsed["FIN"] == 1 and parsed["ACK"] != 0:
                    self.seq = parsed["seq"] + 1
                    syn_ack_fin = bytes([0,parsed["ACK"],0])
                    for _ in range(3):
                        self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, self.destino)
                        time.sleep(0.3)
                    self.socket.close()
                    return
            except:
                print(f"(debug): close - timeout terminado enviando FIN con seq {self.seq}")
                if reenv_fin == 3:
                    self.socket.close()
                    return
                reenv_fin += 1

    def recv_close(self):
        while True:
            req, _ = self.socket.recvfrom(self.buffer)
            parsed = self.parse_segment(req)
            if parsed["FIN"] != 0:
                break
            if parsed["seq"] < self.seq:
                print(f"(debug): recv_close - segmento duplicado con seq {parsed["seq"]}")
                syn_ack_fin = bytes([0,1,0])
                self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, self.destino)
            
        self.seq = parsed["seq"] + 1
        syn_ack_fin = bytes([0,1,parsed["FIN"]])
        reenv_ack = 1
        while True:
            try:
                self.socket.sendto(self.seq.to_bytes(4)+syn_ack_fin, self.destino)
                res, _ = self.socket.recvfrom(self.buffer)
                parsed = self.parse_segment(res)
                if parsed["ACK"] == 1 and parsed["seq"] == (self.seq+1):
                    self.socket.close()
                    return 
            except:
                print(f"(debug): recv_close - timeout terminado enviando ACK+FIN con seq {self.seq}")
                if reenv_ack == 3:
                    self.socket.close()
                    return 
                reenv_ack += 1

        

    