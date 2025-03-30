# network.py
import socket
import sys
from collections import deque
from denial_of_service import is_rate_limited
import socket

PORT = 65432

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

def receive_messages(sock, peer_ip, is_rate_limited, sanitize_message, decrypt_message, key):
    """
    Listens for incoming messages on the UDP socket.

    Args:
        sock (socket): The UDP socket.
        peer_ip (str): The IP address of the connected peer.
        is_rate_limited (function): Function to check message rate.
        sanitize_message (function): Function to process received messages.
        decrypt_message (function): Function to decrypt messages.
        key (bytes): The encryption key.
    """

    message_timestamps = deque(maxlen=5)
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if addr[0] != peer_ip:
                continue
            if is_rate_limited(message_timestamps, 5):
                continue
            decrypted_message = decrypt_message(data, key)
            sanitize_message(decrypted_message.decode())
        except Exception as e:
            print(f"Receive error: {e}")
            break


def send_messages(sock, peer_ip, encrypt_message, key):
    """
    Sends user input messages to a peer device.

    Args:
        sock (socket): The UDP socket.
        peer_ip (str): The IP address of the peer device.
        encrypt_message (function): Function to encrypt messages.
        key (bytes): The encryption key.
    """
    while True:
        try:
            message = input("> ")
            if message.lower() == "exit":
                break
            encrypted_message = encrypt_message(message, key)
            sock.sendto(encrypted_message, (peer_ip, PORT))
        except Exception as e:
            print(f"Send error: {e}")
            break

