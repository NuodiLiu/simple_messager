from datetime import datetime
from src.common.Constants import Constants
from src.server.commands.Command import Command

class ActiveuserCommand(Command):
    COMMAND_LENGTH = 2
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request
    
    def execute(self):
        message = self.createMessage(self.clientThread.getActiveUsers())

        if message is None:
            self.clientThread.messenger.sendToClient(Constants.INFO.NO_ACTIVE_USER)
            print("Info: No other active users")
            return

        self.clientThread.messenger.sendToClient(message)
        print("Info: Active user info sent to client")

    @staticmethod
    def createMessage(activeUsers):
        # format the message
        messageLines = [
            f"{user.username}, {user.activeTime}, {user.clientIPAddress}, {user.clientUDPPort}"
            for user in activeUsers
        ]

        if len(messageLines) == 0:
            return None

        message = '\n'.join(messageLines)
        message = f"{Constants.INFO.ACTIVE_USER}|" + message
        return message
    