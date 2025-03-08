import socket
import sys
import threading
import stun  # Install via: pip install pystun3

RENDEZVOUS_SERVER = ('107.189.20.63', 55555)

# Discover public IP and port using STUN
print("Discovering public IP using STUN...")
nat_type, external_ip, external_port = stun.get_ip_info()

if not external_ip:
    print("Failed to discover public IP. Exiting.")
    sys.exit(1)

print(f"Public IP: {external_ip}, Public Port: {external_port}")

# Connect to rendezvous server
print("Connecting to rendezvous server...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', external_port))  # Bind to discovered port
sock.sendto(f"{external_ip} {external_port}".encode(), RENDEZVOUS_SERVER)

# Wait for peer details
while True:
    data = sock.recv(1024).decode()
    if data.strip() == 'ready':
        print("Checked in with server, waiting...")
        continue
    
    ip, sport, dport = data.split(' ')
    sport, dport = int(sport), int(dport)
    break

print("\nGot peer")
print(f"  IP: {ip}")
print(f"  Source Port: {sport}")
print(f"  Dest Port: {dport}\n")

# Punch hole
print("Punching hole...")
sock.sendto(b'0', (ip, dport))

print("Ready to exchange messages\n")

# Start listener thread
def listen():
    sock_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_listener.bind(('0.0.0.0', external_port))

    while True:
        data = sock_listener.recv(1024)
        print(f"\rPeer: {data.decode()}\n> ", end='')

listener = threading.Thread(target=listen, daemon=True)
listener.start()

# Send messages
while True:
    msg = input('> ')
    sock.sendto(msg.encode(), (ip, sport))
