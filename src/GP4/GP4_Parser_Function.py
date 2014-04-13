# GP4_Parser_Function.py : Parser function Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object

class Parser_Function(AST_object):

    ## Construct new Parser_Function object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the function
    # @param func_body_text : AST object from pyparsing. list of statements.
    # @returns self
    def __init__(self, string, loc, 
                name, func_body_text ):
        
        super(Parser_Function, self).__init__(string, loc, 'parser_function')

        self.name   = name
        self.func_body_text = func_body_text
        self.func   = None  # Python function for this object


    ## Execute the compiled function, giving it the p4 object and the packet to be parsed.
    # @param self : object
    # @param p4   : P4 object
    # @param bits : Bits object
    # @returns fixme
    def execute(self, p4, bits):

        # If we have not yet compiled the function then do so in context of the P4 object
        if not self.func: self.compile_func(p4)


    ## Compile the function in the context of a P4 object (namespace)
    # @param self : object
    # @param p4   : P4 object
    # @returns fixme
    def compile_func(self, p4):

        print "compiling"


    def __str__(self):
        s = self.name + '()'
        return s
