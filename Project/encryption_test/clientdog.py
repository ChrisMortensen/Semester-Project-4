import sys
import subprocess
import json

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
