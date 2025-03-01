import socket

# Port where this server listens for incoming client connections
known_port = 50002

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to port 55555 to listen for client connections
sock.bind(('0.0.0.0', 55555))
# Allow the server to accept connections (backlog of 5 clients)
sock.listen(5)

while True:
    clients = []  # List to store connected clients

    while len(clients) < 2:
        # Accept a new client connection
        conn, address = sock.accept()
        print('Connection from: {}'.format(address))
        clients.append((conn, address))

        # Send a 'ready' message back to the client to acknowledge connection
        conn.sendall(b'ready')
    
    print('Got 2 clients, sending details to each')

    # Extract client details
    c1_conn, c1 = clients.pop()
    c1_addr, _ = c1
    c2_conn, c2 = clients.pop()
    c2_addr, _ = c2

    # Send each client the other's IP address and known port
    c1_conn.sendall('{} {}'.format(c2_addr, known_port).encode())
    c2_conn.sendall('{} {}'.format(c1_addr, known_port).encode())
    
    # Close the connections
    c1_conn.close()
    c2_conn.close()