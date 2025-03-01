import socket
import sys
import threading
import time

# Rendezvous server address (Replace with your actual server)
RENDEZVOUS_SERVER = ('107.189.20.63', 55555)

print("Connecting to rendezvous server...")

# Step 1: Create UDP socket & register with rendezvous server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 0))  # Bind to any available local port

local_port = sock.getsockname()[1]  # Get the actual assigned port
print(f"Local socket bound to: {local_port}")

# Send a registration message to the server
sock.sendto(b'0', RENDEZVOUS_SERVER)

# Step 2: Wait for a "ready" response from the server
while True:
    data, addr = sock.recvfrom(1024)
    if data.decode().strip() == 'ready':
        print("Checked in with server, waiting for peer...")
        break

# Step 3: Receive peer information (IP & ports)
data, addr = sock.recvfrom(1024)
peer_ip, sport, dport = data.decode().split()
sport, dport = int(sport), int(dport)

print(f"\nGot peer details:")
print(f"  Peer IP: {peer_ip}")
print(f"  Source Port (assigned by server): {sport}")
print(f"  Destination Port (peer's listening port): {dport}\n")

# Step 4: Perform UDP Hole Punching
print("Punching hole...")
sock.sendto(b'0', (peer_ip, dport))  # Send an initial packet to peer

# Step 5: Send Keep-Alive Messages to Maintain NAT Mapping
def keep_alive():
    while True:
        sock.sendto(b'keep-alive', (peer_ip, dport))
        time.sleep(10)  # Send every 10 seconds to keep the NAT mapping open

threading.Thread(target=keep_alive, daemon=True).start()

print("Ready to exchange messages!\n")

# Step 6: Start a listener thread for incoming messages
def listen():
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"\rPeer: {data.decode()}\n> ", end='')

listener = threading.Thread(target=listen, daemon=True)
listener.start()

# Step 7: Send messages in a loop
while True:
    msg = input("> ")
    sock.sendto(msg.encode(), (peer_ip, dport))
