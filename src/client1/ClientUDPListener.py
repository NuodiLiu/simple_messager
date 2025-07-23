import threading
import os
from socket import socket
from socket import AF_INET
from socket import SOCK_DGRAM
from src.common.Constants import Constants

class ClientUDPListener(threading.Thread):
    """A class to listen for UDP messages from the server in a separate thread."""

    UDP_IP = "0.0.0.0"
    def __init__(self, clientUDPPort):
        """
        Constructor for the ClientUDPListener class.

        Args:
        - clientUDPPort (int): The UDP port to bind the listener to.
        """
        super().__init__()

        # Initialize the UDP socket
        self.clientUDPPort = clientUDPPort
        self.clientUDPSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientUDPAddress = (ClientUDPListener.UDP_IP, self.clientUDPPort)
        self.clientUDPSocket.bind(self.clientUDPAddress)

    def run(self):
        """Overridden method from Thread. Keeps listening for incoming UDP messages."""
        while True:
            message, _ = self.receiveFromServer()
            self.processReceivedMessage(message)

    def receiveFromServer(self):
        data, addr = self.clientUDPSocket.recvfrom(1024)
        return data, addr
    
    def processReceivedMessage(self, message):
        """
        Process the received message based on its header.

        Args:
        - message (str): The received message.
        """
        # P2P Message is kind of special due to binary data, check first
        # it might be not well designed, but structure is enough for this assignment
        if self.processP2PMessage(message):
            return

        # process other messages based on header
        message = message.decode('utf-8')
        header = message.split("|")[0]
        if (header == Constants.MSG.PRIVATE_MSG):
            time, username, content = message.split("|")[1:]
            print(f"{time}, {username}: {content}")
        elif (header == Constants.MSG.GROUP_MSG):
            time, groupName, username, content = message.split("|")[1:]
            print(f"{time}, {groupName}, {username}: {content}")

    def processP2PMessage(self, message):
        # Extract header values
        CONSTANT_SIZE = 20
        FILENAME_SIZE = 100
        USERNAME_SIZE = 80
        
        constantData = message[:CONSTANT_SIZE].decode('utf-8').strip()
        if constantData != Constants.P2P.P2P_DATA:
            return False
        
        filenameData = message[CONSTANT_SIZE : CONSTANT_SIZE + FILENAME_SIZE].decode('utf-8').strip()
        usernameData = message[CONSTANT_SIZE + FILENAME_SIZE:CONSTANT_SIZE + FILENAME_SIZE + USERNAME_SIZE].decode('utf-8').strip()
        data = message[CONSTANT_SIZE + FILENAME_SIZE + USERNAME_SIZE:]
        self.saveFile(usernameData, filenameData, data)

        return True
    
    @staticmethod
    def saveFile(username, filename, data):
        # dynamically determine where the file is, based on main.py
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        filename = f"{username}_{filename}"
        filePath = os.path.join(currentDirectory, filename)

        with open(filePath, 'ab') as file:
            file.write(data)
            
    def close(self):
        self.clientUDPSocket.close()