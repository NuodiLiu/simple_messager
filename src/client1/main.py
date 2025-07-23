from .Client import Client
import sys

def main():
    """
    Main function to initiate the client program.
    
    Expects command-line arguments for the server IP, server port, and client UDP port.
    Initiates a client instance and starts the client's command loop if login is successful.
    """
    # Ensure the correct number of command-line arguments are provided
    if len(sys.argv) != 4:
        print("\n===== Error usage, python3 Client.py SERVER_IP SERVER_PORT ======\n")
        exit(0)
    
    # Extract server and client details
    serverHost = sys.argv[1]
    serverPort = int(sys.argv[2])
    clientUDPPort = int(sys.argv[3])
    
    # Create a new client instance
    clientInstance = Client(serverHost, serverPort, clientUDPPort)

    # If login is successful, start the client's command loop
    if clientInstance.login():
        clientInstance.commandLoop()

    # Close the connection and terminate the client when commandLoop is stopped
    clientInstance.closeConnection()
    print("\n=====Messager Client will terminate now=====\n")

if __name__ == "__main__":
    main()