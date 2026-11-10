
class RoundRobin:
    routers = dict()

    def add_router_zones(self, routes_file_name: str):
        interfaces = dict()
        
        with open(routes_file_name, 'r', encoding='utf-8') as text:
            routes_file = text.read()
        routes = routes_file.split("\n")
    
        zone = ''
        for route in routes:
            route = route.split(" ")
            actual_zone = f'{route[1]}-{route[2]}'
            if actual_zone == zone:
                interfaces[zone][1] += 1 
            else:
                zone = actual_zone
                interfaces[zone] = [-1, 1]

        router_name = routes_file_name.split("/")[-1].split("_")[1]
        self.routers[router_name] = interfaces
        return router_name
