import socket

def parse_HTTP_message(http_message: bytes):
    # Convertimos el mensaje a string y lo separamos por linea
    message_decoded = http_message.decode()
    message_split = message_decoded.split('\r\n')  

    messageHTTP = dict()
    messageHTTP['start_line'] = message_split[0]

    i = 1
    is_head, is_body = True, False
    while i < len(message_split):
        # Body del mensaje HTTP
        if is_body and message_split[i] != '':
            messageHTTP['body'] = message_split[i]

        # Head del mensaje HTTP
        if is_head and message_split[i] != '':
            header_split = message_split[i].split(':')
            nameHeader = header_split[0]
            contentHeader = header_split[1].strip()
            messageHTTP[nameHeader] = contentHeader
            i += 1

        else:
            is_head, is_body = False, True
            i += 1

    return messageHTTP