# Custom Exception types

import exceptions

class SyntaxError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

