import asyncio
import websockets

# Store connected peers
peers = {}

async def handler(websocket, path):
    global peers

    try:
        peer_id = await websocket.recv()  # First message is the peer's ID
        peers[peer_id] = websocket
        print(f"Peer {peer_id} connected")

        while True:
            message = await websocket.recv()
            target_id, msg = message.split("|", 1)

            if target_id in peers:
                await peers[target_id].send(f"{peer_id}|{msg}")
            else:
                await websocket.send(f"ERROR|Peer {target_id} not found")

    except Exception as e:
        print(f"Peer {peer_id} disconnected: {e}")
    finally:
        del peers[peer_id]

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    await server.wait_closed()

asyncio.run(main())
