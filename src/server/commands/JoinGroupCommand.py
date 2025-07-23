from src.common.Constants import Constants
from src.server.commands.Command import Command

class JoinGroupCommand(Command):
    COMMAND_LENGTH = 2
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request

    def execute(self):
        groupName = self.parseCommand(self.request)
        if groupName is None:
            self.clientThread.messenger.sendToClient(Constants.MSG.ARGU_ERROR)
            print("Group: /joingroup argument error")
            return
        
        print(f"{self.clientThread.user.username} issued '/joingroup {groupName}'")

        if (group := self.server.getGroupByName(groupName)) is None:
            self.clientThread.messenger.sendToClient(Constants.GROUP.NOT_EXIST)
            print(f"Group: Group {groupName} does not exist")
            return
        
        # check if user already exist in the group
        if self.clientThread.user in group.groupMembers:
            self.clientThread.messenger.sendToClient(Constants.GROUP.MEMBER_ALREADY_EXIST)
            print(f"Group: user {self.clientThread.user.username} is already in group {groupName}")
            return

        # add user to the group
        group.addGroupMember(self.clientThread.user)
        self.clientThread.messenger.sendToClient(Constants.GROUP.JOINED)
        print(f"Group: user {self.clientThread.user.username} joined group {groupName}")

    @staticmethod
    def parseCommand(request):
        tokens = request.split(' ')
        if len(tokens) != JoinGroupCommand.COMMAND_LENGTH:
            return None

        return tokens[1]
    
