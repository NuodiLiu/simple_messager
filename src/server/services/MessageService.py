import socket
import sys

class MessageService:
    def __init__(self, clientThread):
        self.clientThread = clientThread

    def receiveFromClient(self):
        try:
            return self.clientThread.TCPSocket.recv(1024).decode()
        except:
            print("Error: fail to receive client message")
            sys.exit()

    def sendToClient(self, message):
        self.clientThread.TCPSocket.sendall(message.encode('utf-8'))

    @staticmethod
    def sendToClientUDP(user, message):
        if user is None:
            return False
        
        # initilize UDP socket for forwarding message/file
        UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # send message
        clientIPAddress = user.clientIPAddress
        clientUDPPort = user.clientUDPPort
        print(f"{user.username}: UDP msg sent to {clientIPAddress}:{clientUDPPort}")
        UDPSocket.sendto(message.encode('utf-8'), (clientIPAddress, clientUDPPort))
        
        # close
        UDPSocket.close()
        return True