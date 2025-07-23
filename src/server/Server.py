import threading
import importlib 
import re
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from src.common.Constants import Constants
from src.server.services.LoggerService import LoggerService

class Server:
    """Server class responsible for managing client connections and server-side functionalities."""

    # static variable that holds clientThread
    activeUserSet = set()
    bannedUserSet = set()
    groupSet = set()

    # Lock to ensure thread safety when modifying class-level sets
    lock = threading.Lock()

    def __init__(self, host, port, MAX_ATTEMPTS):
        """
        Constructor for the Server class.

        Args:
        - host (str): The IP address of the server.
        - port (int): The port number on which the server will listen for incoming connections.
        - MAX_ATTEMPTS (int): Maximum number of login attempts before banning a user.
        """
        self.host = host
        self.port = port
        self.welcomeSocket = socket(AF_INET, SOCK_STREAM)
        self.welcomeSocket.bind((self.host, self.port))
        self.MAX_ATTEMPTS = MAX_ATTEMPTS

        # Initialize logging service
        self.logger = LoggerService()
        self.logger.configLog(Constants.File.USERLOG)
        
    def start(self):
        """Start the server to listen for and accept incoming client connections."""

        print("\n===== Server is running =====")
        print("===== Waiting for connection request from clients...=====")
        while True:
            # Start listening
            self.welcomeSocket.listen()

            # Accept incoming connection and create/start a client thread
            TCPSocket, clientTCPAddress = self.welcomeSocket.accept()
            
            # Dynamically import the ClientThread module to spawn a thread for the client
            ClientThread = importlib.import_module('.ClientThread', 'src.server').ClientThread
            clientThread = ClientThread(self, clientTCPAddress, TCPSocket)
            clientThread.start()

    def getUserByName(self, username):
        return next((user for user in self.activeUserSet if user.username == username), None)

    @classmethod
    def banUser(cls, user):
        with cls.lock:
            cls.bannedUserSet.add(user)
    
    @classmethod
    def unbanUser(cls, user):
        with cls.lock:
            cls.bannedUserSet.remove(user)

    @classmethod
    def addActiveUser(cls, user):
        with cls.lock:
            cls.activeUserSet.add(user)

    @classmethod
    def removeActiveUser(cls, user):
        with cls.lock:
            cls.activeUserSet.remove(user)

    @classmethod
    def createGroup(cls, group):
        cls.groupSet.add(group)

    @classmethod
    def deleteGroup(cls, group):
        cls.groupSet.remove(group)

    @classmethod
    def getGroupByName(cls, groupName):
        with cls.lock:
            return next((group for group in cls.groupSet if group.groupName == groupName), None)
        
    @classmethod
    def getUserByName(cls, username):
        with cls.lock:
            return next((user for user in cls.activeUserSet if user.username == username), None)
        
    @classmethod
    def isUserActive(cls, username):
        return True if cls.getUserByName(username) else False
    
    @staticmethod
    def isGroupNameValid(groupName):
        """
        Check if a group name is valid (only contains alphanumeric characters).

        Args:
        - groupName (str): The name of the group.

        Returns:
        - bool: True if the group name is valid, False otherwise.
        """
        return bool(re.match(r"^[a-zA-Z0-9]+$", groupName))
