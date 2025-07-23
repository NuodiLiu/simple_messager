import sys
import random
import os
import time
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from socket import SOCK_DGRAM
from src.common.Constants import Constants
from .ClientUDPListener import ClientUDPListener

class Client:
    """A client class for connecting, sending and receiving messages to/from a server."""

    # i'm using space to seperate username and password
    illegalCharacters = [' ']

    def __init__(self, serverHost, serverPort, clientUDPPort):
        """
        Constructor for the Client class.

        Args:
        - serverHost (str): The host address of the server.
        - serverPort (int): The port number to connect to the server.
        - clientUDPPort (int): The port for the UDP listener.
        """
        self.username = None
        self.password = None

        # config the client TCP socket
        self.serverHost = serverHost
        self.serverPort = serverPort
        self.clientSocket = socket(AF_INET, SOCK_STREAM)

        # Set up the UDP listener for the client
        self.clientUDPPort = clientUDPPort
        self.clientUDPListener = ClientUDPListener(clientUDPPort)
        self.clientUDPListener.daemon = True
        self.clientUDPListener.start()
    
    def login(self):
        """Initiate the login process to the server."""
        self.connectToServer()
        loginAttempts = 0

        while(True):
            # Promote user input
            self.username = input("Please enter your username: ")
            self.password = input("Please enter your password: ")

            # Check illegal characters
            if (any(char in self.illegalCharacters for char in self.username) or 
                any(char in self.illegalCharacters for char in self.password)):
                print("Illegal characters appears in username or password")
                continue

            # Send credentials to server
            self.sendToServer(f"{self.username} {self.password} {self.clientUDPPort}")
            response = self.receiveFromServer()
            
            # Process server's response
            if (response == Constants.Auth.SUCCESS):
                print("login successful")
                return True
            elif (response == Constants.Auth.FORBIDEN):
                print(f"Please wait for {Constants.Auth.WAITING_TIME} seconds")
                loginAttempts = 0
                break
            elif (response == Constants.Auth.FAIL):
                loginAttempts += 1
                print(f"Login failed for {loginAttempts} times. Try again.")
                continue
            elif (response == Constants.Auth.INVALID_REQUEST):
                print("Please enter invalid username or password")
                continue
            else:
                print("Response error", file=sys.stderr)
                break
            
        return False

    def commandLoop(self):
        print("===== Please type any messsage you want to send to server: =====")
        self.printHelp()
        for inputMessage in sys.stdin:
            # remove the ending newline
            inputMessage = inputMessage.strip()

            # check if command is valid
            if not self.checkValidity(inputMessage):
                continue

            self.sendToServer(inputMessage)
            
            # this will block the for loop and wait
            self.processResponse(self.receiveFromServer())

            # break if logout received
            if inputMessage == Constants.Command.LOGOUT:
                print(f"Bye, {self.username}!")
                break

            self.printHelp()

    def checkValidity(self, inputMessage):
        tokens = inputMessage.split()
        if not tokens:
            print("Error: No command provided")
            return False

        command, *args = tokens

        if command == Constants.Command.MSGTO:
            if len(args) < 2:
                print("Error: Usage: /msgto USERNAME MESSAGE_CONTENT")
                return False
            return True

        elif command == Constants.Command.ACTIVEUSER:
            if len(args) != 0:
                print("Error: Usage: /activeuser")
                return False
            return True
        
        elif command == Constants.Command.CREATEGROUP:
            if (len(args) < 2):
                print("Error: Usage: /creategroup GROUP_NAME USERNAME1 USERNAME2 ...")
                return False
            return True
        
        elif command == Constants.Command.JOINGROUP:
            if (len(args) != 1):
                print("Error: Usage: /joingroup GROUP_NAME")
                return False
            return True
        
        elif command == Constants.Command.GROUPMSG:
            if len(args) < 2:
                print("Error: Usage: /msgto GROUPNAME MESSAGE_CONTENT")
                return False
            return True
        
        elif command == Constants.Command.LOGOUT:
            if len(args) != 0:
                print("Error: Usage: /logout")
                return False
            return True
        
        elif command == Constants.Command.P2PVIDEO:
            if len(args) != 2:
                print("Error: Usage: /p2pvideo USERNAME FILENAME")
                return False
            return True
        
        else:
            print("Error: Invalid command")
            return False

    def processResponse(self, receivedMessage):
        """Process the response and display corresponding message"""
        
        header, *payload = receivedMessage.split('|')
        if header == Constants.MSG.PRIVATE_CON or header == Constants.MSG.GROUP_CON:
            msgCounter, timestamp = payload
            print(f"{header} - No: {msgCounter}, Timestamp: {timestamp}")
        elif header == Constants.MSG.INACTIVE_USER:
            print(f"Failed to send - User is not active")
        elif header == Constants.MSG.ARGU_ERROR:
            print(f"COMMAND: Please use the correct command format")
        elif header == Constants.INFO.NO_ACTIVE_USER:
            print("Info: No other active users")
        elif header == Constants.INFO.ACTIVE_USER:
            print(payload[0])
        elif header == Constants.GROUP.NAME_INVALID:
            print("Group: Invalid group name, only alphanumerical letter allowed")
        elif header == Constants.GROUP.ALREADY_EXIST:
            groupName = payload
            print(f"Group: Group (Name: {groupName}) already exists")
        elif header == Constants.GROUP.CREATED:
            groupName = payload[0]
            usernames = payload[1:]
            print(f"Group chat room has been created, room name: {groupName}, users in this room:")
            for username in usernames:
                print(username, end=" ") 
            print()
        elif header == Constants.GROUP.NOT_EXIST:
            print("Group: Group does not exist")
        elif header == Constants.GROUP.MEMBER_ALREADY_EXIST:
            print("Group: You are already in the group")
        elif header == Constants.GROUP.JOINED:
            print("Group: Group joined successfully")
        elif header == Constants.GROUP.USER_INVALID:
            print("Group: One of the user has invalid name or is offline")
        elif header == Constants.GROUP.MEMBER_NOT_EXIST:
            print("Group: You are not in this group chat")
        elif header == Constants.Auth.SUCCESS:
            print("Auth: Operation succeed")
        elif header == Constants.P2P.P2P_DATA:
            peerIP, peerPort, filename = payload
            # on unpacking, peerPort is str, need to convert to int
            peerPort = int(peerPort)
            self.sendFileToPeerUDP(peerIP, peerPort, filename, self.username)
            
        else:
            print("Unkown response received from server")

    def printHelp(self):
        print("Avaliable commands are: ")
        helpString = ''
        for cmd in dir(Constants.Command):
            # this filters out the built-in attributes/methods
            if cmd.startswith("__"):
                continue
            helpString += getattr(Constants.Command, cmd) + " "
        print(helpString)

    def connectToServer(self):
        self.clientSocket.connect((self.serverHost, self.serverPort))

    def closeConnection(self):
        self.clientSocket.close()

    def closeConnectionUDP(self):
        self.clientUDPListener.close()

    def sendToServer(self, message):
        self.clientSocket.sendall(message.encode('utf-8'))

    def receiveFromServer(self):
        return self.clientSocket.recv(1024).decode('utf-8')

    @staticmethod
    def generateRandomPort():
        return random.randint(49152, 65535)
    
    @staticmethod
    def sendFileToPeerUDP(peerIP, peerUDPPort, filename, username):
        """Send a file to a peer over UDP.

        Args:
        - peerIP (str): The IP address of the peer.
        - peerUDPPort (int): The UDP port of the peer.
        - filename (str): The name of the file to send.
        """
        # size of a packet and less than MTU
        CHUNK_SIZE = 512

        # Fixed length header sizes in bytes
        CONSTANT_SIZE = 20
        FILENAME_SIZE = 100
        USERNAME_SIZE = 80

        # Ensure the input data fits the fixed size
        constantData = Constants.P2P.P2P_DATA.ljust(CONSTANT_SIZE)[:CONSTANT_SIZE]
        filenameData = filename.ljust(FILENAME_SIZE)[:FILENAME_SIZE]
        usernameData = username.ljust(USERNAME_SIZE)[:USERNAME_SIZE]

        # Combine header data
        header = (constantData + filenameData + usernameData).encode('utf-8')

        # dynamically determine where the file is, based on main.py
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(currentDirectory, filename)

        # UDP socket for sending
        UDPSocket = socket(AF_INET, SOCK_DGRAM)

        # read and send the file piece by piece
        try:
            with open(filePath, 'rb') as file:
                while True:
                    data = file.read(CHUNK_SIZE)
                    if not data:
                        break
                    packet = header + data

                    # sleep for 0.1 seconds
                    time.sleep(0.01) 

                    UDPSocket.sendto(packet, (peerIP, peerUDPPort))
            print(f"P2P: {filename} has been sent to peer {peerIP}:{peerUDPPort}")
        except:
            print(f"Cannot Open File: {filename}")
        finally:
            UDPSocket.close()
