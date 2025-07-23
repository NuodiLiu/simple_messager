from src.common.Constants import Constants
from src.server.commands.Command import Command

class MsgToCommand(Command):
    COMMAND_LENGTH = 3
    messageCounter = 1
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request
    
    def execute(self):
        username, content = self.parseCommand(self.request)
        if not username or not content:
            self.clientThread.messenger.sendToClient(Constants.MSG.ARGU_ERROR)
            return
        
        user = self.server.getUserByName(username)
        if user is None:
            self.clientThread.messenger.sendToClient(Constants.MSG.INACTIVE_USER)
            print("Message: failed to send - User is not active")
            return

        # log message to server
        filepath = Constants.File.MESSAGELOG
        self.server.logger.configLog(filepath)
        sequenceNumber = self.server.logger.getSequenceNumber(filepath)
        self.server.logger.logMessage(sequenceNumber, username, content)
        print("Message: log created")

        # send confirmation back to the sender
        confirmation = self.createConfirmation(Constants.MSG.PRIVATE_CON, MsgToCommand.messageCounter)
        self.clientThread.messenger.sendToClient(confirmation)
        MsgToCommand.messageCounter += 1
        print("Message: confirm sent")
    
        # send message content to receiver
        message = self.createMessage(Constants.MSG.PRIVATE_MSG, username, content)
        self.clientThread.messenger.sendToClientUDP(user, message)
        print("Message: msg sent")

    @staticmethod
    def parseCommand(request):
        tokens = request.split(' ', 2)
        if len(tokens) != MsgToCommand.COMMAND_LENGTH:
            return None, None
        _, username, message = tokens
        return username, message