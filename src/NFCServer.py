import sqlite3
import struct
import socket
import time;

from src.DBHandler import DBHandler


class NFCServer:

    AUTH_REQ = 101
    MASTER_REQ = 102
    ADD_TAG = 103
    DELETE_TAG = 104

    def __init__(self, ip_address, port, db_name):
        self.ip_address = ip_address
        self.port = port
        self.address = (self.ip_address, self.port)
        self.sock = ""
        self.server_started = False
        self.master_state = False
        self.db =  DBHandler(db_name)
        self.master_timeout = 10
        self.master_time = 0

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

                if self.master_state:
                    self.check_master_timeout()

                package = self.sock.recvfrom(40)
                p = package[0]
                address = package[1]

                # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.
                code = struct.unpack('>h', p[:2])[0]
                size = struct.unpack('>h', p[2:4])[0]
                data = struct.unpack('>' + 'h' * int(size / 2), p[4:size + 4]) # Replace for get_tag when implemented

                print("Code: {0} Size: {1} Data: {2} Address: {3}".format(code, size, data, address))

    def evaluate_package (self, code, data, address):

        if code == self.MASTER_REQ:
            try:

                if not self.db.check_master_key(data):
                    self.sock.sendto(self.create_package(self.MASTER_REQ, 1, [0]), address)
                    print("Master key not found".format(data))
                else:
                    self.sock.sendto(self.create_package(self.MASTER_REQ, 1, [1]), address)
                    self.master_time = time.time()
                    self.master_state = True
                    print("Master key active".format(data))

            except sqlite3.Error as err:
                self.self.sock.sendto(self.create_package(self.MASTER_REQ, 1, [0]), address)
                print("Data base error: {}".format(err))

        if code == self.AUTH_REQ:

            try:

                if not self.db.check_RFID_tag(data):
                    self.sock.sendto(self.create_package(self.AUTH_REQ, 1, [0]), address)
                    print("Key {} not authorized".format(data))
                else:
                    self.sock.sendto(self.create_package(self.AUTH_REQ, 1, [1]), address)
                    print("Key {} authorized".format(data))

            except sqlite3.Error as err:
                self.self.sock.sendto(self.create_package(self.AUTH_REQ, 1, [0]), address)
                print("Data base error: {}".format(err))

        if code == self.ADD_TAG:

            if self.master_state:

                try:

                    if not self.db.check_RFID_tag(data):
                        self.db.store_rfid_tag(data)
                        self.sock.sendto(self.create_package(self.ADD_TAG, 1, [1]), address)
                        self.master_state = False
                        print("Tag: {} already exists".format(data))
                    else:
                        self.self.sock.sendto(self.create_package(self.ADD_TAG, 1, [1]), address)
                        self.master_state = False
                        print("Tag: {} added successfully".format(data))

                except sqlite3.Error as err:
                    self.self.sock.sendto(self.create_package(self.ADD_TAG, 1, [0]), address)
                    print("Data base error: {}".format(err))
            else:
                self.self.sock.sendto(self.create_package(self.ADD_TAG, 1, [0]), address)
                print("Error adding tag: Master authorization needed")

        if code == self.DELETE_TAG:

            if self.master_state:

                try:

                    if not self.db.check_RFID_tag(data):
                        self.sock.sendto(self.create_package(self.DELETE_TAG, 1, [0]), address)
                        print("Delete error: Tag {} not found".format(data))
                    else:
                        self.db.delte_RFID_tag(data)
                        self.self.sock.sendto(self.create_package(self.DELETE_TAG, 1, [1]), address)
                        self.master_state = False
                        print("Tag: {} deleted successfully".format(data))

                except sqlite3.Error as err:
                    self.self.sock.sendto(self.create_package(self.DELETE_TAG, 1, [0]), address)
                    print("Data base error: {}".format(err))
            else:
                self.self.sock.sendto(self.create_package(self.DELETE_TAG, 1, [0]), address)
                print("Error deleting tag: Master authorization needed")

    def get_tag (self, data):
        pass

    def create_package(self, code, size, data):
        # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.
        code = struct.pack('>h', code)
        size = struct.pack('>h', size)
        data = struct.pack('>' + 'h' * len(data), *data)
        package = code + size + data

        print("Package created -> " + str(package))

        return package

    def check_master_timeout(self):
        if (time.time() - self.master_time) > self.master_timeout:
            self.master_state = False
