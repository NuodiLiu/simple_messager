from src.common.Constants import Constants
class P2PVideoCommand:
    COMMAND_LENGTH = 3
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request

    def execute(self):
        username, filename = self.parseCommand(self.request)
        if username is None or filename is None:
            self.clientThread.messenger.sendToClient(Constants.MSG.ARGU_ERROR)
            print("P2P: /p2pvideo argument error")
            return
        
        user = self.server.getUserByName(username)
        if user is None:
            self.clientThread.messenger.sendToClient(Constants.MSG.INACTIVE_USER)
            print("P2P: targetted user is not active")
            return
        
        # send reponse back via TCP
        message = f"{Constants.P2P.P2P_DATA}|{user.clientIPAddress}|{user.clientUDPPort}|{filename}"
        self.clientThread.messenger.sendToClient(message)
        print("P2P: IP and UDP port sent")
        
    @staticmethod
    def parseCommand(request):
        tokens = request.split(' ')
        if len(tokens) != P2PVideoCommand.COMMAND_LENGTH:
            return None, None

        return tokens[1], tokens[2]