import socket
import sys
import threading

# Address of the rendezvous server (used to facilitate peer-to-peer connection)
rendezvous = ('147.182.184.215', 55555)

# Step 1: Connect to the rendezvous server
print('connecting to rendezvous server')

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to a local port (50001) to receive responses
sock.bind(('0.0.0.0', 50001))
# Send an initial message ('0') to the rendezvous server to check in
sock.sendto(b'0', rendezvous)

# Wait for a response from the server indicating readiness
while True:
    data = sock.recv(1024).decode()
    if data.strip() == 'ready':
        print('checked in with server, waiting')
        break

# Receive peer connection details from the rendezvous server
data = sock.recv(1024).decode()
ip, sport, dport = data.split(' ')
sport = int(sport)  # Source port (our local port for communication)
dport = int(dport)  # Destination port (peer's listening port)

print('\ngot peer')
print('  ip:          {}'.format(ip))
print('  source port: {}'.format(sport))
print('  dest port:   {}\n'.format(dport))

# Step 2: Perform UDP hole punching
# This sends a dummy packet to the peer to establish NAT traversal
print('punching hole')

# Create a new UDP socket for communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind it to our assigned source port (so the peer can recognize us)
sock.bind(('0.0.0.0', sport))
# Send a dummy message ('0') to the peer to establish a connection
sock.sendto(b'0', (ip, dport))

print('ready to exchange messages\n')

# Step 3: Start a listener thread to receive messages from the peer
def listen():
    # Create a new UDP socket to listen for incoming messages
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', sport))  # Bind to our communication port
    
    while True:
        data = sock.recv(1024)  # Receive data from the peer
        print('\rpeer: {}\n> '.format(data.decode()), end='')

# Start the listener thread to receive incoming messages
listener = threading.Thread(target=listen, daemon=True)
listener.start()

# Step 4: Send messages to the peer
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', dport))  # Bind to our destination port

while True:
    msg = input('> ')  # Get user input
    sock.sendto(msg.encode(), (ip, sport))  # Send message to the peer
