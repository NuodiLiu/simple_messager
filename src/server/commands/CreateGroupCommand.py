from src.common.Constants import Constants
from src.server.commands.Command import Command
from src.server.models.Group import Group

class CreateGroupCommand(Command):
    MIN_COMMAND_LENGTH = 2
    def __init__(self, server, clientThread, request):
        self.server = server
        self.clientThread = clientThread
        self.request = request

    def execute(self):
        # Parse the group name from the client's request
        groupName, usernames = self.parseCommand(self.request)
        
        if groupName is None or usernames is None:
            self.clientThread.messenger.sendToClient(Constants.MSG.ARGU_ERROR)
            print("Group: /creategroup argument error")
            return

        print(f"{self.clientThread.user.username} issued '/creategroup {groupName}'")

        # Validate the group name format
        if not self.server.isGroupNameValid(groupName):
            self.clientThread.messenger.sendToClient(Constants.GROUP.NAME_INVALID)
            print("Group: Group name is not valid")
            return

        # Check if a group with the given name already exists
        if (group := self.server.getGroupByName(groupName)) is not None:
            self.clientThread.messenger.sendToClient(f"{Constants.GROUP.ALREADY_EXIST}|{groupName}")
            print("Group: Group already exists")
            return

        # create a new group
        group = Group(groupName, self.clientThread.user)
        # Notify the client that the group was created successfully and create the group
        self.server.createGroup(group)

        # if users are specified, add these users to the group
        userInvalid = False
        if usernames:
            for username in usernames:
                user = self.server.getUserByName(username)
                if user not in self.server.activeUserSet:
                    userInvalid = True
                    break
                group.addGroupMember(user)

        if userInvalid:
            # delete the group created
            self.server.deleteGroup(group)

            # send response back to user
            self.clientThread.messenger.sendToClient(f"{Constants.GROUP.USER_INVALID}|{groupName}|{usernames}")
            print("Group: Group creation failed, some of the users are invalid or offline")
            return

        # contruct username string
        usernameStr = ""
        for name in usernames:
            usernameStr += f"{name}|"
        # get rid of last '|'
        usernameStr [:-1]

        self.clientThread.messenger.sendToClient(f"{Constants.GROUP.CREATED}|{groupName}|{usernameStr}")
        print(f"Group: {self.clientThread.user.username} created {groupName}")

    @staticmethod
    def parseCommand(request):
        tokens = request.split(' ')
        # Less than command length means argument not enough
        if len(tokens) < CreateGroupCommand.MIN_COMMAND_LENGTH:
            return None, None
        
        # If /creategroup groupname appears, return groupname and return users as None
        if len(tokens) == CreateGroupCommand.MIN_COMMAND_LENGTH:
            return tokens[1], None
        
        # both groupname and users are specified in request
        return tokens[1], tokens[2:]