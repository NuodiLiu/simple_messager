import logging
import os
import threading
from datetime import datetime

class LoggerService:
    """Service class for logging various server activities and client interactions."""
    
    lock = threading.Lock()
    def __init__(self):
        pass

    @staticmethod
    def configLog(filepath):
        if not os.path.exists(filepath):
            with open(filepath, 'w') as _:
                pass
        # reset log config
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # change log config
        logging.basicConfig(filename=filepath, level=logging.INFO, format="%(message)s")

    @classmethod
    def getSequenceNumber(cls, filepath):
        with cls.lock:
            with open(filepath, "r") as file:
                return sum(1 for _ in file) + 1

    @classmethod
    def logLogin(cls, sequenceNumer, username, clientIPAddress, clientUDPPort):
        timestamp = datetime.now().strftime("%d %b %Y %H:%M:%S")
        log_entry = f"{sequenceNumer}; {timestamp}; {username}; {clientIPAddress}; {clientUDPPort}"
        with cls.lock:
            logging.info(log_entry)

    @classmethod
    def logMessage(cls, sequenceNumer, username, message):
        timestamp = datetime.now().strftime('%d %b %Y %H:%M:%S')
        logLine = f"{sequenceNumer}; {timestamp}; {username}; {message}"
        with cls.lock:
            logging.info(logLine)