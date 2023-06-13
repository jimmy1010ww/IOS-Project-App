class MoodleCookiesError(Exception):
    def __init__(self):
        message = "Moodle cookies error"
        super().__init__(message)

class MoodleSskeyError(Exception):
    def __init__(self):
        message = "Moodle sskey error"
        super().__init__(message)

class MoodleLoginError(Exception):
    def __init__(self, bot_id:int):
        message = "MoodleBot Login error: {}".format(bot_id)
        super().__init__(message)

class MoodleResponseError(Exception):
    def __init__(self, bot_id:int):
        message = "MoodleBot response error: {}".format(bot_id)
        super().__init__(message)

class MoodleDownloadFileFailed(Exception):
    def __init__(self, bot_id:int):
        message = "MoodleBot download file failed: {}".format(bot_id)
        super().__init__(message)

class MoodleGetPageResourceFailed(Exception):
    def __init__(self, bot_id:int):
        message = "MoodleBot get page resource failed: {}".format(bot_id)
        super().__init__(message)