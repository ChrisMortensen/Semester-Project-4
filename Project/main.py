import socket
import threading
import sys
from collections import deque

import command_injection  
import denial_of_service
import tailscale

PORT = 65432  # Port for communication
MAX_MESSAGES_PER_SECOND = 5  # Maximum allowed messages per second

def receive_messages(sock, peer_ip, is_rate_limited, sanitize_message):
    """
    Listens for incoming messages on the UDP socket.

    Args:
        sock (socket): The UDP socket.
        peer_ip (str): The IP address of the connected peer.
        is_rate_limited (function): Function to check message rate.
        sanitize_message (function): Function to process received messages.
    """
    message_timestamps = deque(maxlen=MAX_MESSAGES_PER_SECOND)  # Stores timestamps of last messages

    while True:
        try:
            data, addr = sock.recvfrom(1024)

            # Ensure message is comming from peer
            if addr[0] != peer_ip:
                continue  # Drop the message

            if is_rate_limited(message_timestamps, MAX_MESSAGES_PER_SECOND): # Rate limiting (denial_of_service.py)
                continue  # Drop the message

            message = data.decode()
            sanitize_message(message) # Sanitizing (Command_injection.py)
            
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

def main():
    """
    Main function for the program.

    - Determines the Tailscale binary path based on the OS.
    - Retrieves and displays available Tailscale devices.
    - Allows the user to select a device.
    - Establishes a UDP connection with the selected peer.
    - Starts separate threads for receiving and sending messages.

    Exits:
        If no devices are found or if any critical error occurs.
    """
    # Determine the correct Tailscale path based on OS
    tailscale_path = tailscale.get_tailscale_path(sys.platform)

    # Get the list of available Tailscale devices
    devices = tailscale.get_tailscale_devices(tailscale_path)
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
    recv_thread = threading.Thread(target=receive_messages, args=(sock, peer_ip, denial_of_service.is_rate_limited, command_injection.process_peer_message))
    recv_thread.daemon = True
    recv_thread.start()

    # Start sending messages
    send_messages(sock, peer_ip)

    # Close socket after exiting
    sock.close()

# Allows us to use this file as an executable script (run directly) 
# and reusable module (imported into another script).
if __name__ == "__main__":
    main()