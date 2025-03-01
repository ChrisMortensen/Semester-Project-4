import socket

# Port where this server listens for incoming client connections
known_port = 50002

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to port 55555 to listen for client messages
sock.bind(('0.0.0.0', 55555))

while True:
    clients = []  # List to store connected clients

    while True:
        # Receive a message from a client
        data, address = sock.recvfrom(128)

        print('connection from: {}'.format(address))
        clients.append(address)  # Store client address

        # Send a 'ready' message back to the client to acknowledge connection
        sock.sendto(b'ready', address)

        # Once we have two clients, we can facilitate the peer-to-peer connection
        if len(clients) == 2:
            print('got 2 clients, sending details to each')
            break

    # Extract client details
    c1 = clients.pop()
    c1_addr, c1_port = c1
    c2 = clients.pop()
    c2_addr, c2_port = c2

    # Send each client the other's IP address and port
    # This allows them to attempt a direct connection (UDP hole punching)
    sock.sendto('{} {} {}'.format(c1_addr, c1_port, known_port).encode(), c2)
    sock.sendto('{} {} {}'.format(c2_addr, c2_port, known_port).encode(), c1)