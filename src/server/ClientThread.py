import threading
from datetime import datetime
from datetime import timedelta
from src.common.Constants import Constants
from src.server.models.User import User
from src.server.commands.MsgToCommand import MsgToCommand
from src.server.commands.ActiveuserCommand import ActiveuserCommand
from src.server.commands.CreateGroupCommand import CreateGroupCommand
from src.server.commands.JoinGroupCommand import JoinGroupCommand
from src.server.commands.GroupMsgCommand import GroupMsgCommand
from src.server.commands.LogoutCommand import LogoutCommand
from src.server.commands.P2PVideoCommand import P2PVideoCommand
from src.server.services.MessageService import MessageService

class ClientThread(threading.Thread):
    """A class to handle individual client connections in separate threads."""

    def __init__(self, server, clientTCPAddress, TCPSocket):
        """Initialize the ClientThread instance.
        
        Args:
            server (Server): The main server instance.
            clientTCPAddress (tuple): A tuple containing the client's IP and TCP port.
            TCPSocket (socket): The client's socket.
        """
        super().__init__()
        self.server = server
        self.loginAttempts = 0
        self.clientIPAddress = clientTCPAddress[0]
        self.clientTCPPort = clientTCPAddress[1]
        self.TCPSocket = TCPSocket
        self.clientAlive = False
        self.user = None
        self.messenger = MessageService(self)

        print("===== New connection created for: ", clientTCPAddress)
        self.clientAlive = True
        
    def run(self):
        """Thread's main execution method. Listens for client commands and processes them."""

        # Check for authentication
        if not self.authenticate():
            print("Authentication failed")
            print(f"Client {self.clientIPAddress, self.clientTCPPort} disconnected")
            self.TCPSocket.close()
            return
        
        self.clientAlive = True

        sequenceNumber = self.server.logger.getSequenceNumber(Constants.File.USERLOG)
        self.server.logger.logLogin(sequenceNumber, self.user.username, self.clientIPAddress, self.clientUDPPort)
        
        while self.clientAlive:
            request = self.messenger.receiveFromClient()
            print(request)
            if request.startswith(Constants.Command.MSGTO):
                command = MsgToCommand(self.server, self, request)
            elif request.startswith(Constants.Command.ACTIVEUSER):
                command = ActiveuserCommand(self.server, self, request)
            elif request.startswith(Constants.Command.CREATEGROUP):
                command = CreateGroupCommand(self.server, self, request)
            elif request.startswith(Constants.Command.JOINGROUP):
                command = JoinGroupCommand(self.server, self, request)
            elif request.startswith(Constants.Command.GROUPMSG):
                command = GroupMsgCommand(self.server, self, request)
            elif request.startswith(Constants.Command.LOGOUT):
                command = LogoutCommand(self.server, self, request)
            elif request.startswith(Constants.Command.P2PVIDEO):
                command = P2PVideoCommand(self.server, self, request)
            elif request in [' ', '', '\n']:
                continue
            else:
                print("FATAL: No command received at server")
                continue

            command.execute()

        print(f"Client {self.clientIPAddress, self.clientTCPPort} disconnected")
        self.TCPSocket.close()
        return

    @staticmethod
    def readCredentialFile():
        """Reads the credential file and returns a list of username-password tuples.

        Returns:
            list[tuple]: List containing tuples of (username, password).
        """

        with open(Constants.File.CREDENTIALS, 'r') as file:
            return [tuple(line.strip().split()) for line in file]
            
    def getActiveUsers(self):
        """Returns a list of active users excluding the current user.

        Returns:
            list[User]: List of active User objects.
        """

        return [user for user in self.server.activeUserSet if user.username != self.user.username]

    def parseCredentials(self, credentials: str):
        """Parses and returns the user credentials from the provided string.

        Args:
            credentials (str): The string containing username, password, and client UDP port.

        Returns:
            tuple: Contains parsed username, password, and client UDP port.

        Raises:
            ValueError: If the input format is incorrect.
        """

        try:
            username, password, clientUDPPort = credentials.split()
            return username, password, int(clientUDPPort)
        except ValueError:
            raise ValueError("Invalid input. Please provide both username and password.")
    
    def authenticate(self):
        """Authenticate the client based on the provided credentials.

        Returns:
            bool: True if the client is authenticated successfully, otherwise False.
        """

        while self.loginAttempts <= self.server.MAX_ATTEMPTS:
            try:
                username, password, self.clientUDPPort = self.parseCredentials(self.messenger.receiveFromClient())
            except ValueError:
                self.messenger.sendToClient(Constants.Auth.INVALID_REQUEST)
                print(f"authenticate: cannot parse tokens")
                continue

            # Check if user is temporarily banned based on time
            receiveTime = datetime.now()
            usersToUnban = []
            for user in self.server.bannedUserSet:
                if user.username == username and user.bannedTime is not None:
                    if (receiveTime - user.bannedTime) < timedelta(seconds=Constants.Auth.WAITING_TIME):
                        self.messenger.sendToClient(Constants.Auth.FORBIDEN)
                        print(f"authenticate: {user.username} is currently banned")
                        return False
                    elif receiveTime - user.bannedTime >= timedelta(seconds=Constants.Auth.WAITING_TIME):
                        usersToUnban.append(user)
                        print(f"authenticate: {user.username} unbanned")

            for user in usersToUnban:
                self.server.unbanUser(user)

            # Successfully authenticated
            if (username, password) in ClientThread.readCredentialFile():
                self.user = User(username, self.TCPSocket, self.clientIPAddress, self.clientTCPPort, self.clientUDPPort)
                self.server.addActiveUser(self.user)
                self.messenger.sendToClient(Constants.Auth.SUCCESS)
                print(f"authenticate: {username} login succeed")
                return True

            # If max attempts are reached, temporarily ban the user
            if self.loginAttempts >= self.server.MAX_ATTEMPTS:
                # create and ban user
                self.user = User(username, self.TCPSocket, self.clientIPAddress, self.clientTCPPort, self.clientUDPPort, bannedTime=datetime.now())
                self.server.banUser(self.user)
                # Reset attempts
                self.loginAttempts = 0  
                self.messenger.sendToClient(Constants.Auth.FORBIDEN)
                print(f"authenticate: {username} banned")
                return False
            else:
                # Failure to authenticate
                self.loginAttempts += 1
                self.messenger.sendToClient(Constants.Auth.FAIL)
                print(f"authenticate: {username} failed {self.loginAttempts} times")
        return False