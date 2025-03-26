import socket
import threading
import sys
import subprocess
import json
from collections import deque

import command_injection  
import denial_of_service

MACOS_TAILSCALE_PATH = "/Applications/Tailscale.app/Contents/MacOS/tailscale"
WINDOWS_TAILSCALE_PATH = "C:/Program Files/Tailscale/tailscale.exe"
PORT = 65432  # Port for communication
MAX_MESSAGES_PER_SECOND = 5  # Maximum allowed messages per second

def get_tailscale_path(platform):
    """
    Returns the path to the Tailscale binary based on the OS.

    Args:
        platform (str): The OS identifier.

    Returns:
        str: The full path to the Tailscale executable.
    """
    if platform.startswith("win"):
        return WINDOWS_TAILSCALE_PATH
    elif platform.startswith("darwin"):
        return MACOS_TAILSCALE_PATH
    else:
        print("Unsupported OS")
        sys.exit(1)

def get_tailscale_devices(tailscale_path):
    """
    Retrieves and returns a list of available Tailscale devices.
    
    Returns:
        list: A list of tuples containing (hostname, IP address)
    """
    try:
        result = subprocess.run([tailscale_path, "status", "--json"], capture_output=True, text=True, check=True)
        status = json.loads(result.stdout)

        devices = []
        for peer in status.get("Peer", {}).values():
            if peer.get("Online"):
                hostname = peer.get("DNSName").split(".tail")[0]
                tailscale_ips = peer.get("TailscaleIPs", [])

                # Extract the first IPv4 address
                tail_addr = next((ip for ip in tailscale_ips if "." in ip), None)

                if hostname and tail_addr:
                    devices.append((hostname, tail_addr))

        return devices
    
    except Exception as e:
        print(f"Error getting Tailscale devices: {e}")
        return []

def receive_messages(conn, peer_ip):
    """
    Listens for incoming messages on the UDP socket.

    Args:
        sock (socket): The UDP socket.
        peer_ip (str): The IP address of the connected peer.
        is_rate_limited (function): Function to check message rate.
        sanitize_message (function): Function to process received messages.
    """
    message_timestamps = deque(maxlen=MAX_MESSAGES_PER_SECOND)  

    while True:
        try:
            data = conn.recv(1024)  # Receive message
            if not data:
                break  # Exit if connection is closed

            if denial_of_service.is_rate_limited(message_timestamps, MAX_MESSAGES_PER_SECOND):
                continue  # Drop message if rate limit exceeded

            message = data.decode()
            command_injection.process_peer_message(message)  # Process message securely
            
        except Exception as e:
            print(f"Receive error: {e}")
            break


def send_messages(conn):
    """
    Sends user input messages to a peer device.

    Args:
        conn (socket): The TCP connection.
    """
    while True:
        try:
            message = input("> ")
            if message.lower() == "exit":
                break
            conn.send(message.encode())  

        except Exception as e:
            print(f"Send error: {e}")
            break
        
def print_devices(devices):
    """
    Prints the device on the Tailscale network.

    Args:
        devices (list): The list of devices on the Tailscale network.
    """
    print("\nAvailable Tailscale Devices:")
    max_name_length = max(len(name) for name, _ in devices) # Find the longest name
    for idx, (name, ip) in enumerate(devices, start=1):
        print(f"{idx}. {name.ljust(max_name_length)} | {ip}")

def get_device_choice(devices):
    """
     Prompts the user to select a device from the provided Tailscale device list.

    Args:
        devices (list): The list of devices on the Tailscale network.
    """
    while True:
        try:
            choice = int(input("\nSelect a device (number): "))
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            else:
                print("Invalid choice. Try again.")

        except ValueError:
            print("Please enter a valid number.")

def create_tcp_socket():
    """
    Creates and binds a TCP socket to receive messages.
    
    Returns:
        socket.socket: The created and bound TCP socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind to all interfaces and listen for incoming connections
    try:
        sock.bind(("0.0.0.0", PORT))
        sock.listen(1)  # Allow only one connection at a time
        return sock
    except OSError as e:
        print(f"Port binding error: {e}")
        sys.exit(1)

def run_tailscale():
    """
    Initializes and runs the Tailscale peer-to-peer communication.

    - Determines the Tailscale binary path based on the OS.
    - Retrieves and displays available Tailscale devices.
    - Allows the user to select a device.
    - Establishes a UDP connection with the selected peer.
    - Starts separate threads for receiving and sending messages.

    Exits:
        If no devices are found or if any critical error occurs.
    """
    tailscale_path = get_tailscale_path(sys.platform)
    devices = get_tailscale_devices(tailscale_path)
    if not devices:
        print("No available Tailscale devices found.")
        sys.exit(1)

    print_devices(devices)
    device_name, peer_ip = get_device_choice(devices)

    sock = create_tcp_socket()
    print(f"\nWaiting for a connection from {device_name} ({peer_ip})...")

    sock.settimeout(30)  
    try:
        conn, addr = sock.accept()
        print(f"Connected to {addr}")

        recv_thread = threading.Thread(target=receive_messages, args=(conn, peer_ip))
        recv_thread.daemon = True
        recv_thread.start()

        send_messages(conn)
        conn.close()  
    except socket.timeout:
        print("Connection timeout.")
        sys.exit(1)

    sock.close()

# Allows us to use this file as an executable script (run directly) 
# and reusable module (imported into another script).
if __name__ == "__main__":
    run_tailscale()