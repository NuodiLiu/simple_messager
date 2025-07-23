class Group:
    def __init__(self, groupName, creator):
        self.groupName = groupName
        self.groupMembers = {creator}

    def addGroupMember(self, user):
        self.groupMembers.add(user)      

    def removeGroupMember(self, user):
        """
        this while loop ensures all repeated join will be removed
        might be better to use a set here but spec says creator must be 
        at the begining of member list
        """
        while user in self.groupMembers:
            self.groupMembers.remove(user)