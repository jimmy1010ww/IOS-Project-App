class InvalidRequestMethod(Exception):
    def __init__(self):
        message = "Invalid request method"
        super().__init__(message)

class UserIDNotExist(Exception):
    def __init__(self, _userid):
        message = "Userid: {} not exist".format(_userid)
        super().__init__(message)

class InvalidReceiveData(Exception):
    def __init__(self, _message):
        message = "Invalid receive data: {}".format(_message)
        super().__init__(message)

class InvalidPostParameter(Exception):
    def __init__(self, _message):
        message = "Invalid post parameter: {}".format(_message)
        super().__init__(message)

class MoodleBotError(Exception):
    def __init__(self, _message):
        message = "MoodleBot error: {}".format(_message)
        super().__init__(message)