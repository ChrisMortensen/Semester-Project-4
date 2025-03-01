SERVER_HOST = "127.0.0.1"
SERVER_PORT = 1234

import socket

clientToRelayServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientToRelayServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print(f"Connecting to RELAY SERVER @ {SERVER_HOST}:{SERVER_PORT}...\n")
clientToRelayServer.connect((SERVER_HOST, SERVER_PORT))

print("> Local connection to RELAY SERVER:", clientToRelayServer.getsockname())

portThatClientUsedToConnectToMainServer = clientToRelayServer.getsockname()[1]
peerServerListeningAddress = ("0.0.0.0", portThatClientUsedToConnectToMainServer)
myPeerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myPeerServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("> Starting P2P server on", peerServerListeningAddress)
myPeerServer.bind(peerServerListeningAddress)
myPeerServer.listen()

import select
import time

readList = [clientToRelayServer, myPeerServer]

while True:
  conns, _, _ = select.select(readList, [], [], 1)
  for connection in conns:
    if connection is myPeerServer:
      newConnection, clientToRelayServer_address = myPeerServer.accept()
      readList.append(newConnection)
      print("P2P | New connection from", clientToRelayServer_address)
      
    elif connection is clientToRelayServer:
      data = connection.recv(4096)
      if not data:
        print("RELAY | Server closed.")
        readList.remove(clientToRelayServer)
      else:
        # Naively assume the data is an address tuple
        host, port = data.decode().split("|")
        port = int(port)
        print("RELAY | Got peer address:", (host,port))
        print(f"| Going to connect to {host}:{port}!")
        newClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newClient.connect((host,port))
        newClient.send(b"Hey ;)")
    else:
      data = connection.recv(4096)
      if not data:
        print("Peer | A connection was closed.")
        readList.remove(connection)
      else:
        print("Peer | Data:", data.decode())
  time.sleep(1)