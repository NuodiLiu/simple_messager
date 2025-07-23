import os

class Constants:
    class Auth:
        REQUEST = "AUTH_REQUEST"
        DATA = "AUTH_DATA"
        SUCCESS = "AUTH_SUCCESS"
        FAIL = "AUTH_FAIL"
        FORBIDEN = "AUTH_FORBIDEN"
        ILLEGAL_CHARS = "AUTH_ILLEGAL_CHARS"
        INVALID_REQUEST = "AUTH_INVALID_REQUEST"
        MAX_ATTEMPTS = 5
        WAITING_TIME = 10
    class MSG:
        ARGU_ERROR = "ARGUMENT_ERROR"
        INACTIVE_USER = "MSG_INACTIVE_USER"
        PRIVATE_MSG = "PRIVATE_MSG"
        PRIVATE_CON = "PRIVATE_CON"
        GROUP_MSG = "GROUP_MSG"
        GROUP_CON = "GROUP_CREATE_CONFIRMATION"
    class INFO:
        ACTIVE_USER = "ACTIVE_USER"
        NO_ACTIVE_USER = "NO_ACTIVE_USER"
    class GROUP:
        ALREADY_EXIST = "GROUP_ALREADY_EXIST"
        NOT_EXIST = "GROUP_NOT_EXIST"
        CREATED = "GROUP_CREATED"
        NAME_INVALID = "GROUP_NAME_INVALID"
        MEMBER_ALREADY_EXIST = "GROUP_MEMBER_ALREADY_EXIST"
        MEMBER_NOT_EXIST = "GROUP_MEMBER_NOT_EXIST"
        USER_INVALID = "GROUP_USER_INVALID"
        JOINED = "GROUP_MEMBER_JOINED" 
    class P2P:
        P2P_DATA = "P2P_DATA"
    class File:
        LOGDIR = "logs"
        SERVERDIR = "src/server"
        USERLOG = os.path.join(LOGDIR, 'userlog.txt')
        MESSAGELOG = os.path.join(LOGDIR, 'messagelog.txt')
        CREDENTIALS = os.path.join(SERVERDIR, 'credentials.txt')
    class Command:
        MSGTO = "/msgto"
        ACTIVEUSER = "/activeuser"
        CREATEGROUP = "/creategroup"
        JOINGROUP = "/joingroup"
        GROUPMSG = "/groupmsg"
        LOGOUT = "/logout"
        P2PVIDEO = "/p2pvideo"