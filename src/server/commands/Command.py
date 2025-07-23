from datetime import datetime
class Command:
    def execute(self):
        pass

    @staticmethod
    def createMessage(messageType, targetName, content):
        return f"{messageType}|{datetime.now().strftime('%d/%m/%Y %H:%M')}|{targetName}|{content}"
    
    @staticmethod
    def createGroupMessage(messageType, targetGroupName, targetName, content):
        return f"{messageType}|{datetime.now().strftime('%d/%m/%Y %H:%M')}|{targetGroupName}|{targetName}|{content}"
    
    @staticmethod
    def createConfirmation(messageType, msgCounter):
        timestamp = datetime.now().strftime('%d %b %Y %H:%M:%S')
        return f"{messageType}|{msgCounter}|{timestamp}"