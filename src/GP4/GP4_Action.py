# GP4_Action.py : P4 Action Object
#
## @package GP4

from GP4_Utilities  import *
#from GP4_Parser_Function_Code import *
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

class Action(AST_object):

    ## Construct new Action object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the Action
    # @returns self
    def __init__(self, string, loc, name ):
        
        super(Action, self).__init__(string, loc, 'action')

        self.name = name


