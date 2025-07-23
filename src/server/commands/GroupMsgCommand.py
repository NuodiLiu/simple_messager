import os
from src.common.Constants import Constants
from src.server.commands.Command import Command

class GroupMsgCommand(Command):
    COMMAND_LENGTH = 3
    messageCounter = 1
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request

    def execute(self):
        groupName, content = self.parseCommand(self.request)

        if (group := self.server.getGroupByName(groupName)) is None:
            self.clientThread.messenger.sendToClient(Constants.GROUP.NOT_EXIST)
            print(f"Group: Group {groupName} does not exist")
            return
        
        # check if user exist in the group
        if self.clientThread.user not in group.groupMembers:
            self.clientThread.messenger.sendToClient(Constants.GROUP.MEMBER_NOT_EXIST)
            print(f"Group: user {self.clientThread.user.username} is not in group {groupName}")
            return

        # log message to server
        filepath = os.path.join(Constants.File.LOGDIR, f"{group.groupName}_messageLog.txt")
        self.server.logger.configLog(filepath)
        sequenceNumber = self.server.logger.getSequenceNumber(filepath)
        self.server.logger.logMessage(sequenceNumber, self.clientThread.user.username, content)
        print("Message: log created")

        # stop if no other active members in the group
        if len(group.groupMembers) == 1:
            return
        
        # send message to all other members
        message = self.createGroupMessage(Constants.MSG.GROUP_MSG, groupName, self.clientThread.user.username ,content)
        for member in group.groupMembers:
            self.clientThread.messenger.sendToClientUDP(member, message)
        print("Message: msg sent to other group members")

        # send confirmation back to the sender
        confirmation = self.createConfirmation(Constants.MSG.GROUP_CON, GroupMsgCommand.messageCounter)
        self.clientThread.messenger.sendToClient(confirmation)
        GroupMsgCommand.messageCounter += 1
        print("Message: confirm sent")

    @staticmethod
    def parseCommand(request):
        tokens = request.split(' ', 2)
        if len(tokens) != GroupMsgCommand.COMMAND_LENGTH:
            return None, None
        _, username, message = tokens
        return username, message
    
    
