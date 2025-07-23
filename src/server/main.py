import sys
from src.server.Server import Server
from src.common.Constants import Constants

def main():
    """
    Main function to initiate the server program.
    
    Expects command-line arguments for the server port and maximum login attempts.
    Initiates a server instance and starts the server.
    """

    # Ensure the correct number of command-line arguments are provided
    if len(sys.argv) != 3:
        print("\n===== Error usage, python3 main.py SERVER_PORT ======\n")
        exit(0)

    # Extract server details and maximum login attempts from command-line arguments
    serverIP = '127.0.0.1'
    serverPort = int(sys.argv[1])
    MAX_ATTEMPTS = int(sys.argv[2])

    # Create a new server instance and start the server
    serverInstance = Server(serverIP, serverPort, MAX_ATTEMPTS)
    serverInstance.start()

if __name__ == '__main__':
    main()
    
