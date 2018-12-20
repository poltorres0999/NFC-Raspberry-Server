import RPi.GPIO as GPIO
import MFRC522
import signal
import socket
import struct

class NFCClient:

    AUTH_REQ = 101
    MASTER_REQ = 102
    ADD_TAG = 103
    DELETE_TAG = 104

    START_MASTER = 8
    ADD_TAG_B = 10
    DELETE_TAG_B = 12

    def __init__(self, port, ip_addres):

        self.ip_address = ip_addres
        self.port = port
        self.server_address = (self.ip_address, self.port)
        self.master_state = False
        self.client_timeout = 5
        self.sock = ""
        self.card_reader = MFRC522.MFRC522()

    def init_client(self):

        try:
            print("Starting NFC client ...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Socket creation: Socket created!")
            self.sock.settimeout(self.client_timeout)
            print("Client started!")

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.START_MASTER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.ADD_TAG_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.DELETE_TAG_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        except socket.error as err:
            print("Error starting client: {}".format(err))

    def run_client(self):

        while (True):

            card_uid = self.read_card()

            if card_uid:

                if self.master_state:
                    pass
                else:
                    self.handle_authentication(card_uid)


    def read_card(self):

        # Scan for cards
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print("Card detected")

        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            return uid

    @staticmethod
    def __create_package(code, size, data):
        # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.
        code = struct.pack('>h', code)
        size = struct.pack('>h', size)
        data = struct.pack('>' + 'h' * len(data), *data)
        package = code + size + data

        print("Package created -> " + str(package))

        return package

    def handle_authentication(self, card_uid):

        package = self.__create_package(self.AUTH_REQ, 8, card_uid)
        self.sock.sendto(package, self.server_address)
        response = self.handle_server_response()

        if response == 1:
            print("AUTHENTICATED")
        else:
            print ("AUTHENTICATION FAILED")

    def handle_server_response(self):

        try:

            package = self.sock.recvfrom(40)
            p = package[0]
            address = package[1]

            if address == self.active_device or self.active_device == "":
                print("Received {} bytes from {}".format(len(package), address))

                # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.

                code = struct.unpack('>h', p[:2])[0]
                size = struct.unpack('>h', p[2:4])[0]
                data = struct.unpack('>' + 'h' * int(size / 2), p[4:size + 4])

                return data

        except socket.timeout as err:
            print("Socket err: ", err)
            print("SERVER RESPONSE TIMED OUT\n")
            self.run_client()

    def authenticate_master(self, master_key):

        package = self.__create_package(self.MASTER_REQ, 8, master_key)
        self.sock.sendto(package, self.server_address)
        response = self.handle_server_response()

        if response == 1:
            print("MASTER KEY AUTHENTICATED")
            return True
        else:
            print("AUTHENTICATION MASTER KEY FAILED")
            return False

    def handle_master_state(self):
        button_activated = False
        master_authenticated = self.authenticate_master()

        if master_authenticated:
            """ Si el master es correcte, esperem fins que es premi un polsador, per escriure o esborrar """

            while(in_timeout):

                add_tag = GPIO.input(self.ADD_TAG)
                delete_tag = GPIO.input(self.DELETE_TAG)

                if not add_tag:
                    package = self.__create_package(self.MASTER_REQ, 8, master_key)
                    self.sock.sendto(package, self.server_address)
                    button_activated = True


                if not delete_tag:
                    package = self.__create_package(self.AD, 8, master_key)
                    self.sock.sendto(package, self.server_address)
                    button_activated = True

            if button_activated:

                response = self.handle_server_response()

                if response == 1:
                    print("ADD/DELETE successful")
                    return True
                else:
                    print("FAILED ADDING/DELETING")
                    return False
            else:
                print("No action button pressed")
                self.master_state = False
                self.run_client()
        else:
            self.master_state = False
            self.run_client()








