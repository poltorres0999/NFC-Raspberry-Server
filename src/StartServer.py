from NFCServer import NFCServer

server_ip = "192.168.1.160"
server_port = 4445

server = NFCServer(server_ip, server_port, "rfid-db")
server.start_server()
server.start_listening()
