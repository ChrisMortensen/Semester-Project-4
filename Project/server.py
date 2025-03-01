def tupleToDelimString(tup):
  # ("a", 2, "c") -> "a|2|c"
  return "|".join([str(item) for item in tup])
  
import socket

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((LISTEN_IP, LISTEN_PORT))

server.listen()
print(f"Server listening on {LISTEN_IP}:{LISTEN_PORT}")

clients = []

while len(clients) < 2:
  connection, client_address = server.accept()
  print("New connection from", client_address)
  clients.append(connection)

print("Two clients have connected. Exchanging details for P2P")
clients[0].send(tupleToDelimString(clients[1].getpeername()).encode())
clients[1].send(tupleToDelimString(clients[0].getpeername()).encode())

print("Exit!")
#clients[0].close()
#clients[1].close()
