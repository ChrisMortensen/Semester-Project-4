import asyncio
import websockets
import socket
import threading

SIGNALING_SERVER = "ws://107.189.20.63:8765"  # Change to your server IP
LOCAL_PORT = 5000  # Port for P2P connection

peer_id = input("Enter your peer ID: ")
target_id = input("Enter the target peer ID: ")

async def signaling_client():
    async with websockets.connect(SIGNALING_SERVER) as ws:
        await ws.send(peer_id)  # Send peer ID to server

        while True:
            message = await ws.recv()
            sender_id, data = message.split("|", 1)

            print(f"Signaling: {sender_id} -> {data}")

            if data.startswith("CONNECT"):
                peer_ip = data.split(":")[1]
                print(f"Trying to connect to {peer_ip}")
                connect_to_peer(peer_ip)

async def send_message():
    while True:
        msg = input("Message: ")
        if msg.lower() == "exit":
            break
        await send_via_signaling(f"{target_id}|CONNECT:{get_local_ip()}")
        send_to_peer(msg)

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

def connect_to_peer(ip):
    global peer_socket
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.connect((ip, LOCAL_PORT))
    print(f"Connected to peer {ip}")

    thread = threading.Thread(target=receive_from_peer)
    thread.start()

def send_to_peer(msg):
    peer_socket.sendall(msg.encode())

def receive_from_peer():
    while True:
        try:
            data = peer_socket.recv(1024)
            if not data:
                break
            print(f"Peer: {data.decode()}")
        except:
            break

async def send_via_signaling(msg):
    async with websockets.connect(SIGNALING_SERVER) as ws:
        await ws.send(peer_id)
        await ws.send(msg)

async def main():
    threading.Thread(target=asyncio.run, args=(send_message(),)).start()
    await signaling_client()

asyncio.run(main())
