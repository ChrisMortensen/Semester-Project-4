import os
import subprocess
import re

# The following message attempts to create a "Malware.txt" file on the receiver's PC:
# Example malicious input: hello && echo "Malware" > Malware.txt

IS_SAFE = True  # FOR TESTING PURPOSES. DO NOT PUSH WHEN FALSE!
ERROR_ON_INJECTION = True # Subprocess method errors, while the regex method prints the failed injection to peer.

def safe_method_subprocess(message):
    """
    Safe Method 1, Subprocess:
    This ensures the message is treated as an argument, not executed as a command.
    """
    subprocess.run(["echo", "Peer:", message], shell=False)

def safe_method_sanitization(message):
    """
    Safe Method 2, Sanitizing:
    Uses regex to remove non-printable ASCII.
    """
    sanitized_message = re.sub(r'[^\x20-\x7E]', '', message)
    print(f"Peer: {sanitized_message}")

def unsafe_method_os_system(message):
    """
    Unsafe Method, Vulnerable to command injection:
    Executing message in command without validating message.
    """
    os.system(f"echo Peer: {message}")

def process_peer_message(message):
    """
    Processes the incoming message.
    """
    if IS_SAFE:
        if ERROR_ON_INJECTION:
            safe_method_subprocess(message)
        else:
            safe_method_sanitization(message)
    else:
        unsafe_method_os_system(message)