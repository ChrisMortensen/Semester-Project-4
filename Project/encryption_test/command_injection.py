import os
import subprocess

IS_SAFE = False

def process_peer_message(message):
    """
    Function to process a message, demonstrating a command injection vulnerability.
    """
    # The following message tries to make a Malware file on the receivers pc:
    # hello && echo "Malware" > Malware.txt

    # This is just a single safe / unsafe example, try to find more
    if IS_SAFE:  # Safe execution
        subprocess.run(["echo", "Peer:", message], shell=False)
    else:  # Vulnerable execution
        os.system(f"echo Peer: {message}")  # Potential command injection