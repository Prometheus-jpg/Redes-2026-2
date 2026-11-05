
def check_routes(routes_file_name: str, destination_address: tuple[str, int]): 
    (ip_destino, puerto_destino) = destination_address

    with open(routes_file_name, 'r', encoding='utf-8') as text:
        routes_file = text.read()
    routes = routes_file.split("\n")
    
    for route in routes:
        route_split = route.split(" ")
        ip_cidr = route_split[0]
        puerto_inicial = int(route_split[1])
        puerto_final = int(route_split[2])
        if puerto_inicial <= puerto_destino <= puerto_final:
            (next_hop_IP, next_hop_puerto) = (route_split[3], int(route_split[4]))
            return (next_hop_IP, next_hop_puerto)
    
    return None