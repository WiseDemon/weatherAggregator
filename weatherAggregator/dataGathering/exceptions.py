class FetchError(Exception):
    """Error when fetching data from weather source"""
    def __init__(self, msg=None):
        if msg is None:
            msg = 'FetchError'
        else:
            msg = 'FetchError: ' + msg
        super().__init__(msg)


class NoApiKeysError(Exception):
    """Api keys were not set"""
    def __init__(self, msg=None):
        if msg is None:
            msg = 'NoApiKeysError'
        else:
            msg = 'NoApiKeysError: ' + msg
        super().__init__(msg)


class SourceNotSupportedError(Exception):
    """No function for fetching data from that source"""
    def __init__(self, msg=None):
        if msg is None:
            msg = 'SourceNotSupprotedError'
        else:
            msg = 'SourceNotSupprotedError: ' + msg
        super().__init__(msg)
