import sys
import subprocess
import json

MACOS_TAILSCALE_PATH = "/Applications/Tailscale.app/Contents/MacOS/tailscale"
WINDOWS_TAILSCALE_PATH = "C:/Program Files/Tailscale/tailscale.exe"
LINUX_TAILSCALE_PATH = "/usr/bin/tailscale"

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
    elif platform.startswith("linux"):
        return LINUX_TAILSCALE_PATH
    else:
        print("Unsupported OS")
        sys.exit(1)

def get_tailscale_devices():
    """
    Retrieves and returns a list of available Tailscale devices.
    
    Returns:
        list: A list of tuples containing (hostname, IP address)
    """
    tailscale_path = get_tailscale_path(sys.platform)
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
