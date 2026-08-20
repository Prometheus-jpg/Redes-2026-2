import socket

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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind(new_socket_address)
    server_socket.listen(3)

    print('... Esperando clientes')
    while True:
        new_socket, new_socket_address = server_socket.accept()

        recv_message = new_socket.recv(buff_size)
        
        while recv_message.find(b'\r\n\r\n') == -1:
            recv_message += new_socket.recv(buff_size)

        parsed = parse_HTTP_message(recv_message)
        if 'body' in parsed.keys():
            while len(parsed['body']) < parsed['Content-Length']:
                recv_message += new_socket.recv(buff_size)
                parsed = parse_HTTP_message(recv_message)

        parsed['start_line'] = parsed['start_line'].split(" ")[-1] + ' 200 OK'
        parsed['Content-Type'] = 'text/html; charset=UTF-8'

        with open('res.html', 'r', encoding='utf-8') as html:
            html_str = html.read()
        
        parsed['Content-Length'] = str(len(html_str.encode()))
        
        parsed['body'] = html_str.encode()
        parsed['X-ElQuePregunta'] = "Ricardo Ogno"

        response_message = create_HTTP_message(parsed)
        new_socket.send(response_message)

        new_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")