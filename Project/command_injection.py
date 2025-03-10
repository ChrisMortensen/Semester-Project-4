import os
import subprocess

IS_SAFE = False

# Get input (What is received from peer)
message = input("> ")  
    # The following message tries to make a Malware file on the receivers pc:
    # hello && echo "Malware" > Malware.txt

# This is just 2 examples, try to find more
if IS_SAFE: # Safe
    # Run the command safely without shell=True
    subprocess.run(["echo", "Peer:", message], shell=False)
else:    # Not Safe
    os.system(f"echo Peer: {message}")  # Can be escaped