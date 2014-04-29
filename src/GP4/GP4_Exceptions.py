# GP4_Exceptions.py
## @package GP4
# Custom Exception types

import exceptions

class SyntaxError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

class InternalError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

class RuntimeError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

class InsufficientBytesRuntimeError(exceptions.Exception):
    def __init__(self, args = None):
        self.args = args

