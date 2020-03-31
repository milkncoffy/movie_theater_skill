class FailedRequestError(BaseException):
    def __init__(self, url, msg=None):
        if msg is None:
            msg = 'Request to {} failed'.format(url)
        super(FailedRequestError, self).__init__(msg)


class UnexpectedPageStructureError(BaseException):
    def __init__(self, url, msg=None):
        if msg is None:
            msg = 'Error during parsing {}. Unexpected HTML-structure'.format(url)
        super(UnexpectedPageStructureError, self).__init__(msg)