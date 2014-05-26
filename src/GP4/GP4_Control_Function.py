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

    ## Execute the code associated with this function
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @returns None
    def execute( self, p4 ):
        if not self.func:
            print self.name, "Compiling code..."
            self.compile_code( p4 )
        print self.name, "executing..."
        self.func( p4 )

    ## Compile the code associated with this function and save as self.func
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @returns None
    def compile_code( self, p4 ):
        code = 'def f(p4):\n'
        
        for stmt in self.ctrl_body_text:
            stmt_codeL =  self.compile_stmt( stmt, p4 )
            for new_stmt in stmt_codeL:
                code += '   ' + new_stmt + '\n'

        print "code is", code

        try:
            exec code
        except Exception as ex_err:
            print "Error: generated code for python function yielded exception:",ex_err.data
            print "code was <\n",code,"\n>\n"
            raise GP4_Exceptions.RuntimeError, ex_err.data

        self.func = f


    ## Compile the code associated with one statement and return list of code for it.
    # @param self : Control_Function object
    # @param stmt : Pyparsing control_statement object
    # @param p4   : p4 object
    # @returns codeL : list of Strings implementing python code for this statement.
    def compile_stmt( self, stmt, p4 ):
        return [ 'print "code for fun %s\\n"' % self.name ]
       




    def __str__(self):
        s = self.name + '()'
        return s
