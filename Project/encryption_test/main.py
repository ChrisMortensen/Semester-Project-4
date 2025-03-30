import sys
import threading
from security import ECDHKeyExchange, encrypt_message, decrypt_message
import command_injection
import denial_of_service
from clientdog import get_tailscale_devices, get_tailscale_path, get_device_choice, print_devices
from network import create_udp_socket, receive_messages, send_messages

PORT = 65432

def run_tailscale():
    tailscale_path = get_tailscale_path(sys.platform)
    devices = get_tailscale_devices(tailscale_path)
    if not devices:
        print("No available Tailscale devices found.")
        sys.exit(1)

    print_devices(devices)
    device_name, peer_ip = get_device_choice(devices)
    sock = create_udp_socket()
    print(f"\nConnected to {device_name} ({peer_ip})")

    # Initialize ECDH key exchange
    ecdh = ECDHKeyExchange()
    public_key = ecdh.get_public_key()

    # Send public key
    sock.sendto(public_key, (peer_ip, PORT))
    peer_public_key, _ = sock.recvfrom(4096)
    print(f"Received Peer Public Key: {peer_public_key.decode()}")

    # Generate shared secret
    shared_secret = ecdh.generate_shared_secret(peer_public_key)
    print("Secure channel established!")

    # Start threads
    recv_thread = threading.Thread(target=receive_messages, args=(
        sock, peer_ip, denial_of_service.is_rate_limited, command_injection.process_peer_message, decrypt_message, shared_secret))
    recv_thread.daemon = True
    recv_thread.start()

    send_messages(sock, peer_ip, encrypt_message, shared_secret)
    sock.close()


if __name__ == "__main__":
    run_tailscale()