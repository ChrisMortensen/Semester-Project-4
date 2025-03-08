import socket

KNOWN_PORT = 50002  # Port for hole punching

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 55555))

while True:
    clients = []

    while len(clients) < 2:
        data, address = sock.recvfrom(128)
        public_ip, public_port = data.decode().split(' ')
        public_port = int(public_port)

        print(f"Connection from {public_ip}:{public_port}")
        clients.append((public_ip, public_port))

        sock.sendto(b'ready', (public_ip, public_port))

    # Assign peers
    c1_ip, c1_port = clients.pop()
    c2_ip, c2_port = clients.pop()

    print("Got 2 clients, sending details to each")

    sock.sendto(f"{c1_ip} {c1_port} {KNOWN_PORT}".encode(), (c2_ip, c2_port))
    sock.sendto(f"{c2_ip} {c2_port} {KNOWN_PORT}".encode(), (c1_ip, c1_port))
