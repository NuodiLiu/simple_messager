from datetime import datetime

class User:
    def __init__(self, username, TCPSocket, clientIPAddress, clientTCPPort, clientUDPPort, isActive=True, activeTime=None, bannedTime=None):
        self.username = username
        self.isActive = isActive
        self.activeTime = activeTime if activeTime is not None else datetime.now()
        self.bannedTime = bannedTime
        self.TCPSocket = TCPSocket
        self.clientIPAddress = clientIPAddress
        self.clientTCPPort = clientTCPPort
        self.clientUDPPort = clientUDPPort
