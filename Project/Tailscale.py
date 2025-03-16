import socket
import threading
import sys
import subprocess
import json

import command_injection  

MACOS_TAILSCALE_PATH = "/Applications/Tailscale.app/Contents/MacOS/tailscale"
WINDOWS_TAILSCALE_PATH = "C:/Program Files/Tailscale/tailscale.exe"
PORT = 65432  # Port for communication

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

def receive_messages(sock, callback):
    """
    Listens for incoming messages on the UDP socket.

    Args:
        sock (socket): The UDP socket.
        callback (function): Function to process received messages.
    """
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            message = data.decode()
            
            # Use function from command_injection.py
            callback(message)
            
        except Exception as e:
            print(f"Receive error: {e}")
            break

def send_messages(sock, peer_ip):
    """
    Sends user input messages to a peer device.

    Args:
        sock (socket): The UDP socket.
        peer_ip (str): The IP address of the peer device.
    """
    while True:
        try:
            message = input("> ")
            if message.lower() == "exit":
                break
            sock.sendto(message.encode(), (peer_ip, PORT))

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

def create_udp_socket():
    """
    Creates and binds a UDP socket to receive messages.

    Returns:
        socket.socket: The created and bound UDP socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to all interfaces to receive messages
    try:
        sock.bind(("0.0.0.0", PORT))
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
    # Determine the correct Tailscale path based on OS
    tailscale_path = get_tailscale_path(sys.platform)

    # Get the list of available Tailscale devices
    devices = get_tailscale_devices(tailscale_path)
    if not devices:
        print("No available Tailscale devices found.")
        sys.exit(1)

    # Display devices and let user pick one
    print_devices(devices)
    device_name, peer_ip = get_device_choice(devices)

    # Create a UDP socket
    sock = create_udp_socket()
    print(f"\nConnected to {device_name} ({peer_ip})")

    # Start the receive thread
    recv_thread = threading.Thread(target=receive_messages, args=(sock, command_injection.process_peer_message))
    recv_thread.daemon = True
    recv_thread.start()

    # Start sending messages
    send_messages(sock, peer_ip)

    # Close socket after exiting
    sock.close()

# Allows us to use this file as an executable script (run directly) 
# and reusable module (imported into another script).
if __name__ == "__main__":
    run_tailscale()