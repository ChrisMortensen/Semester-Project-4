import socket
import threading
import sys
import subprocess
import json

PORT = 65432  # Port for communication

# Function to get all available Tailscale devices
def get_tailscale_devices():
    try:
        result = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True, check=True)
        status = json.loads(result.stdout)

        devices = []
        for peer in status.get("Peer", {}).values():
            if peer.get("Online"):
                hostname = peer.get("HostName")
                tailscale_ips = peer.get("TailscaleIPs", [])

                # Extract the first IPv4 address
                tail_addr = next((ip for ip in tailscale_ips if "." in ip), None)

                if hostname and tail_addr:
                    devices.append((hostname, tail_addr))

        return devices
    except Exception as e:
        print(f"Error getting Tailscale devices: {e}")
        return []

# Function to receive messages
def receive_messages(sock):
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            print(f"\nPeer: {data.decode()}\n> ", end="", flush=True)
        except Exception as e:
            print(f"Receive error: {e}")
            break

# Function to send messages
def send_messages(sock, peer_ip):
    while True:
        try:
            message = input("> ")
            if message.lower() == "exit":
                break
            sock.sendto(message.encode(), (peer_ip, PORT))
        except Exception as e:
            print(f"Send error: {e}")
            break

# Get the list of available Tailscale devices
devices = get_tailscale_devices()

if not devices:
    print("No available Tailscale devices found.")
    sys.exit(1)

# Display devices and let user pick one
print("\nAvailable Tailscale Devices:")
for idx, (name, ip) in enumerate(devices, start=1):
    print(f"{idx}. {name} ({ip})")

while True:
    try:
        choice = int(input("\nSelect a device (number): "))
        if 1 <= choice <= len(devices):
            device_name, peer_ip = devices[choice - 1]
            break
        else:
            print("Invalid choice. Try again.")
    except ValueError:
        print("Please enter a valid number.")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to all interfaces to receive messages
try:
    sock.bind(("0.0.0.0", PORT))
except OSError as e:
    print(f"Port binding error: {e}")
    sys.exit(1)

print(f"\nConnected to {device_name} ({peer_ip})")

# Start the receive thread
recv_thread = threading.Thread(target=receive_messages, args=(sock,))
recv_thread.daemon = True
recv_thread.start()

# Start sending messages
send_messages(sock, peer_ip)

# Close socket after exiting
sock.close()
