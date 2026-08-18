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
        elif key == 'body':
            final_message += b'\r\n'
            final_message += value
            has_body = True
        else:
            # Los headers son del tipo 'Nombre-del-header: contenido del header'
            final_message += key.encode() + b': ' + value.encode() + b'\r\n'
    if not has_body:
        final_message += b'\r\n'

    # Retornamos el mensaje HTTP en bytes
    return final_message