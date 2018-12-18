import struct
import socket

class NFCServer:

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.address = (self.ip_address, self.port)
        self.sock = ""
        self.server_started = False

    def start_server(self):

        if not self.server_started:

            try:
                print("Starting server ...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("Socket creation: Socket created!")
                self.sock.bind(self.address)
                print("Socket binding: Socket bound!")
                self.server_started = True
                print("Server started!")

            except socket.error as err:
                print("Error starting server: {}".format(err))

    def start_listening(self):

        if self.server_started:
            print("Start listening, waiting for data")

            while self.server_started:

                try:

                    package = self.sock.recvfrom(40)
                    p = package[0]
                    address = package[1]

                    # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.
                    code = struct.unpack('>h', p[:2])[0]
                    size = struct.unpack('>h', p[2:4])[0]
                    data = struct.unpack('>' + 'h' * int(size / 2), p[4:size + 4])

                    print("Code: {0} Size: {1} Data: {2} Address: {3}".format(code, size, data, address))




