import socket

# Port where this server listens for incoming client connections
SERVER_PORT = 55555

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', SERVER_PORT))

print(f"Rendezvous server listening on port {SERVER_PORT}...")

clients = {}  # Dictionary to store connected clients

while True:
    # Receive a message from a client
    data, address = sock.recvfrom(128)
    
    if address in clients:
        print(f"Duplicate connection from: {address}, ignoring...")
        continue  # Ignore duplicate registrations

    print(f"New client registered: {address}")
    clients[address] = True  # Store client info

    # Send a 'ready' message back to the client
    sock.sendto(b'ready', address)

    # Wait until two unique clients are connected
    if len(clients) >= 2:
        print("Two clients connected, facilitating peer-to-peer connection...")
        break

# Extract client details
c1, c2 = list(clients.keys())[:2]
c1_ip, c1_port = c1
c2_ip, c2_port = c2

print(f"Client 1: {c1_ip}:{c1_port}")
print(f"Client 2: {c2_ip}:{c2_port}")

# Step 1: Send each client the other's **public** IP & port (NAT-aware)
sock.sendto(f"{c2_ip} {c2_port} {c1_port}".encode(), c1)
sock.sendto(f"{c1_ip} {c1_port} {c2_port}".encode(), c2)

# Clear clients to handle new connections
