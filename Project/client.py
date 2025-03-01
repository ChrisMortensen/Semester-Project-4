import socket
import threading

rendezvous = ('107.189.20.63', 55555)  # Address of the rendezvous server

# Step 1: Connect to the rendezvous server
print('Connecting to rendezvous server...')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(rendezvous)  # Establish TCP connection with the server

# Wait for a response from the server
response = sock.recv(1024).decode()
if response.strip() == 'ready':
    print('Checked in with server, waiting for peer...')

# Receive peer details
data = sock.recv(1024).decode()
ip, port = data.split(' ')
port = int(port)

print(f'Got peer: {ip}:{port}\n')

# Step 2: Connect to the peer
peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
peer_sock.connect((ip, port))  # Establish direct TCP connection
print('Connected to peer. Ready to exchange messages.\n')

# Function to listen for incoming messages
def listen():
    while True:
        data = peer_sock.recv(1024).decode()
        if not data:
            break
        print(f'\rPeer: {data}\n> ', end='')

# Start a listening thread
listener = threading.Thread(target=listen, daemon=True)
listener.start()

# Step 3: Send messages to the peer
while True:
    msg = input('> ')
    peer_sock.sendall(msg.encode())  # Send message to peer