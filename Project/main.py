import socket
import threading
import sys
from collections import deque

import command_injection  
import denial_of_service
import tailscale
import security

PORT = 65432  # Port for communication
MAX_MESSAGES_PER_SECOND = 5  # Maximum allowed messages per second

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

def create_tcp_socket(peer_type, port=None):
    """
    Creates a TCP socket for either a client or a server.

    Args:
        peer_type (str): "server" or "client" to specify socket behavior.
        port (int, optional): The port number (only required for the server).

    Returns:
        socket.socket: The created TCP socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if peer_type.lower() == "server":
        if port is None:
            raise ValueError("Port must be specified for a server socket.")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(1)

    return sock

def try_connect_or_listen(host, port):
    """
    Attempts to connect to a peer first, then switches to listening if it fails.

    Args:
        host (str): The IP address of the peer.
        port (int): The port to use.

    Returns:
        socket.socket: The connected socket.
    """
    sock = create_tcp_socket("client")
    sock.settimeout(2)

    try:
        sock.connect((host, port))
        print("Connected as client.")
        sock.settimeout(None)  # Ensure blocking mode for receiving
        return sock
    except (socket.error, ConnectionRefusedError):
        sock.close()

    # If connection failed, become the "server"-peer
    server_sock = create_tcp_socket("server", port)
    print("Waiting for peer to connect...")
    
    conn, addr = server_sock.accept()
    print(f"Accepted connection from {addr}")
    conn.settimeout(None)  # Ensure blocking mode

    server_sock.close()  # We no longer need the listening socket
    return conn

def receive_messages(sock, key, is_rate_limited, sanitize_message):
    """
    Listens for incoming messages on the TCP socket.

    Args:
        sock (socket): The TCP socket.
        key (bytes): The decryption key.
        is_rate_limited (function): Function to check message rate.
        sanitize_message (function): Function to process received messages.
    """
    message_timestamps = deque(maxlen=MAX_MESSAGES_PER_SECOND)

    buffer = ""

    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("Connection closed by peer.")
                break
            
            message = security.decrypt_message(message, key)

            buffer += data
            while "\n" in buffer:  # Process complete messages
                message, buffer = buffer.split("\n", 1)

                if is_rate_limited(message_timestamps, MAX_MESSAGES_PER_SECOND): # Rate limiting (denial_of_service.py)
                    continue

                sanitize_message(message) # Sanitizing (Command_injection.py)

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Receive error: {e}")
            break

def send_messages(sock, key):
    """
    Sends user input messages to a peer device over TCP.

    Args:
        sock (socket): The TCP socket.
        key (bytes): The decryption key.
    """
    while True:
        try:
            message = input("> ")
            if message.lower() == "exit":
                break
            message = message + "\n"
            message = security.encrypt_message(message, key)
            sock.sendall(message.encode())  # Ensure full message is sent
        except Exception as e:
            print(f"Send error: {e}")
            break

def key_exchange(sock):
    '''
    Example text

    Args:
        sock (socket): The TCP socket.
    '''
    #Create public and private key
    ecdh = security.ECDHKeyExchange()
    public_key = ecdh.get_public_key()

    #Sending public key to peer
    print(public_key)
    sock.sendall(public_key)

    #Recieve peer public key
    peer_public_key = sock.recv(4096)
    print(peer_public_key)

    # Generate shared secret from the peer's public key
    shared_secret = ecdh.generate_shared_secret(peer_public_key)
    print("Secure channel established!")
    return shared_secret



def main():
    """
    Main function for the program.

    - Retrieves and displays available Tailscale devices.
    - Allows the user to select a device.
    - Establishes a TCP connection with the selected peer.
    - Starts separate threads for receiving and sending messages.

    Exits:
        If no devices are found or if any critical error occurs.
    """

    # Get the list of available Tailscale devices
    devices = tailscale.get_tailscale_devices()
    if not devices:
        print("No available Tailscale devices found.")
        sys.exit(1)

    # Display devices and let user pick one
    print_devices(devices)
    device_name, peer_ip = get_device_choice(devices)

    # Establish TCP connection
    sock = try_connect_or_listen(peer_ip, PORT)
    print(f"\nConnected to {device_name} ({peer_ip})")

    # Key exchange
    key = key_exchange(sock)

    # Start the receive thread
    recv_thread = threading.Thread(target=receive_messages, args=(sock, key, denial_of_service.is_rate_limited, command_injection.process_peer_message))
    recv_thread.daemon = True
    recv_thread.start()

    # Start sending messages
    send_messages(sock, key)

    # Close socket after exiting
    sock.close()

# Allows us to use this file as an executable script (run directly) 
# and reusable module (imported into another script).
if __name__ == "__main__":
    main()