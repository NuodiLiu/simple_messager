from src.common.Constants import Constants
class LogoutCommand:
    COMMAND_LENGTH = 1
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request

    def execute(self):
        # remove user from ActiveUserSet
        self.server.removeActiveUser(self.clientThread.user)

        # remove user from all groups
        for group in self.server.groupSet:
            group.removeGroupMember(self.clientThread.user)

        # set user as inactive to close the thread on server
        self.clientThread.clientAlive = False

        # delete user from log
        self.deleteUserFromLog(self.clientThread.user.username, Constants.File.USERLOG)
        print(f"Authenticate: user {self.clientThread.user.username} logout")

        # send back confirmation to terminal client loop
        self.clientThread.messenger.sendToClient(Constants.Auth.SUCCESS)

    @staticmethod
    def deleteUserFromLog(username, logfile):
        with open(logfile, 'r') as file:
            lines = file.readlines()

        # find the user line and remove it
        lines = [line for line in lines if line.split(";")[2].strip() != username]

        # adjust sequence numbers
        for i, line in enumerate(lines):
            parts = line.split(";")
            parts[0] = str(i + 1)
            lines[i] = ";".join(parts)

        # write data back
        with open(logfile, 'w') as file:
            file.writelines(lines)