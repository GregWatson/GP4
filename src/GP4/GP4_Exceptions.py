# GP4_Exceptions.py
## @package GP4
# Custom Exception types
#
# self.args has special meaning, but doesnt seem ro print correctly, so using self.data instead.

import exceptions

class SyntaxError(exceptions.Exception):
    def __init__(self, args = None):
        self.data = args

class InternalError(exceptions.Exception):
    def __init__(self, args = None):
        self.data = args

class RuntimeError(exceptions.Exception):
    def __init__(self, args = None):
        self.data = args
    
class InsufficientBytesRuntimeError(exceptions.Exception):
    def __init__(self, args = None):
        self.data = args

class RuntimeParseError(exceptions.Exception):
    def __init__(self, args = None):
        self.data = args

