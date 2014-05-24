# GP4_Control_Function.py : P4 Control function Object
#
## @package GP4

from GP4_Utilities  import *
#from GP4_Parser_Function_Code import *
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

class Control_Function(AST_object):

    ## Construct new Control_Function object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the Control function
    # @param ctrl_body_text : AST object from pyparsing. List of statements.
    # @returns self
    def __init__(self, string, loc, 
                name, ctrl_body_text ):
        
        super(Control_Function, self).__init__(string, loc, 'control_function')

        self.name   = name
        self.ctrl_body_text = ctrl_body_text
        self.func   = None  # Python function for this object

    def __str__(self):
        s = self.name + '()'
        return s
