import json


class Response(object):
    def __init__(self, text="<html></html>", url="", status_code=600, error_msg=''):
        self.text = text
        # self.content = text.encode("utf-8")
        self.status_code = status_code
        self.url = url
        self.error_msg = error_msg

    def json(self):
        return self.text