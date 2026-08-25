import socket
import json

def parse_HTTP_message(http_message: bytes):
    # separamos el mensaje por linea
    message_split = http_message.split(b'\r\n')  

    messageHTTP = dict()
    messageHTTP['start_line'] = message_split[0].decode()

    i = 1
    is_head, is_body = True, False
    while i < len(message_split):
        # Body del mensaje HTTP se guarda en bytes
        if is_body and message_split[i] != b'':
            messageHTTP['body'] = message_split[i]

        # Head del mensaje HTTP
        if is_head and message_split[i] != b'':
            message_decoded = message_split[i].decode()
            header_split = message_decoded.split(': ')
            nameHeader = header_split[0]
            contentHeader = header_split[1].strip()
            messageHTTP[nameHeader] = contentHeader
            i += 1

        else:
            is_head, is_body = False, True
            i += 1

    return messageHTTP

def create_HTTP_message(http_message_parsed):
    final_message = b''

    has_body = False
    for key, value in http_message_parsed.items():
        if key == 'start_line':
            # La start line es unicamente el valor ya que no tiene nombre de header dentro del HEAD
            start_line = value
            final_message += start_line.encode() + b'\r\n'
        elif key != 'body':
            # Los headers son del tipo 'Nombre-del-header: contenido del header'
            final_message += key.encode() + b': ' + value.encode() + b'\r\n'
        else:
            has_body = True

    final_message += b'\r\n'        
    if has_body:
        final_message += http_message_parsed['body']

    # Retornamos el mensaje HTTP en bytes
    return final_message


if __name__ == "__main__":
    buff_size = 30
    new_socket_address = ('localhost', 8000)

    print('Creando socket - Servidor')
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    proxy_socket.bind(new_socket_address)
    proxy_socket.listen(3)

    print('... Esperando clientes')
    while True:
        client_socket, client_socket_address = proxy_socket.accept()

        recv_message = client_socket.recv(buff_size)
        
        while recv_message.find(b'\r\n\r\n') == -1:
            recv_message += client_socket.recv(buff_size)

        parsed = parse_HTTP_message(recv_message)
        if 'body' in parsed.keys():
            while len(parsed['body']) < int(parsed['Content-Length']):
                recv_message += client_socket.recv(buff_size)
                parsed = parse_HTTP_message(recv_message)

        with open('proxy_forb.json') as file:
            data = json.load(file)
            blocked_dom = data['blocked']

        if parsed['start_line'].split( )[0] == 'CONNECT': #Solo nos importa HTTP Request
            continue
        elif parsed['start_line'].find('/gatito-LoP.jpg') != -1: #GET de la imagen
            parsed['start_line'] = parsed['start_line'].split(" ")[-1] + ' 200 OK'
            parsed['Content-Type'] = 'image/jpg'
            with open('gatito-LoP.jpg', 'rb') as file:
                img = file.read()
            parsed['Content-Length'] = str(len(img))
            parsed['body'] = img
            
        elif parsed['start_line'].split( )[1][7:] in blocked_dom:
            parsed['start_line'] = parsed['start_line'].split(" ")[-1] + ' 403 FORBIDDEN'
            parsed['Content-Type'] = 'text/html; charset=UTF-8'
            with open('forbidden.html', 'r', encoding='utf-8') as html:
                html_str = html.read()
            parsed['Content-Length'] = str(len(html_str.encode()))
            parsed['body'] = html_str.encode()

        else:
            IP_server = parsed['Host']
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((IP_server, 80))

            parsed['X-ElQuePregunta'] = 'Ricardo Ogno'
            response_server = create_HTTP_message(parsed)
            server_socket.send(response_server)

            recv_server_message = server_socket.recv(buff_size)
            while recv_server_message.find(b'\r\n\r\n') == -1:
                recv_server_message += server_socket.recv(buff_size)
            
            parsed = parse_HTTP_message(recv_server_message)
            if 'Content-Length' in parsed.keys():
                while len(parsed['body']) < int(parsed['Content-Length']):
                    recv_server_message += server_socket.recv(buff_size)
                    parsed = parse_HTTP_message(recv_server_message)

            server_socket.close()
            print(f"conexión con server ha sido cerrada")

        with open('proxy_forb.json') as file:
            data = json.load(file)
            for word in data['forbidden_words']:
                for key, item in word.items():
                    parsed['body'] = parsed['body'].replace(key.encode(), item.encode())
        parsed['Content-Length'] = str(len(parsed['body']))

        redirect_message = create_HTTP_message(parsed)
        client_socket.send(redirect_message)

        client_socket.close()
        print(f"conexión con cliente {client_socket_address} ha sido cerrada")