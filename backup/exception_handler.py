import logging
from flask import jsonify

class exception_handler:
    def __init__(self, logger:logging.Logger):
        self.logger = logger
    
    # 處理 exception 的 message
    def handle_exception_message(self, _message:str):
        self.logger.error(_message)

    # 處理 success 的 message
    def handle_success_message(self, _message):
        self.logger.info(_message)