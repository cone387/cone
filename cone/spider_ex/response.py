
class Response(object):
    TIMEOUT = 600
    PROXY_ERROR = 700
    ERROR = 800

    def __init__(self, text="<html></html>", url="", status_code=600, error_msg=''):
        self.text = text
        self.content = b'<html></html>'
        self.status_code = status_code
        self.url = url
        self.error_msg = error_msg
        self.content = b''

    def json(self):
        return {'url': self.url, 'status_code': self.status_code}

    @property
    def is_proxy_error(self):
        return self.status_code == self.PROXY_ERROR

    @property
    def is_timeout(self):
        return self.status_code == self.TIMEOUT


def dump(filename='test.html'):
    def dump_wrapper(method):
        def method_wrapper(_, response: Response):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return method(_, response)
        return method_wrapper
    return dump_wrapper
