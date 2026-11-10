from RoundRobin import RoundRobin

def check_routes(routes_file_name: str, destination_address: tuple[str, int], roundRobin: tuple[RoundRobin, str]): 
    (ip_destino, puerto_destino) = destination_address

    with open(routes_file_name, 'r', encoding='utf-8') as text:
        routes_file = text.read()
    routes = routes_file.split("\n")
    interfaces = roundRobin[0].routers[roundRobin[1]]

    for i in range(len(routes)):
        route_split = routes[i].split(" ")
        ip_cidr = route_split[0]
        puerto_inicial = int(route_split[1])
        puerto_final = int(route_split[2])
        if puerto_inicial <= puerto_destino <= puerto_final:
            next_hop_i = interfaces[f'{puerto_inicial}-{puerto_final}']
            next_hop_i[0] = (next_hop_i[0] + 1) % next_hop_i[1]
            interfaces[f'{puerto_inicial}-{puerto_final}'][0] = next_hop_i[0]

            next_route = routes[i + next_hop_i[0]].split(" ")
            (next_hop_IP, next_hop_puerto) = (next_route[3], int(next_route[4]))
            return (next_hop_IP, next_hop_puerto)
    
    return None