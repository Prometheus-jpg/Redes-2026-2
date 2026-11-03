import sys

if len(sys.argv) < 4:
    print("Se debe pasar el IP, puerto y archivo con las rutas del router como argumentos.")
    sys.exit(1)
else:
    router_IP = sys.argv[1]
    router_puerto = sys.argv[2]
    router_rutas_path = sys.argv[3]