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
        
        codeL = self.generate_body_code( p4, self.ctrl_body_text)
        for new_stmt in codeL:
            code += '   ' + new_stmt + '\n'

        print "code is", code

        try:
            exec code
        except Exception as ex_err:
            print "Error: generated code for python function yielded exception:",ex_err.data
            print "code was <\n",code,"\n>\n"
            raise GP4_Exceptions.RuntimeError, ex_err.data

        self.func = f

    ## Generate the code associated with a list of control statements
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @param body : list of Pyparsing control_statement objects
    # @returns List of strings implementing the code
    def generate_body_code( self, p4, body ):
        codeL = []
        for stmt in body:
            codeL.extend( self.compile_stmt( stmt, p4 ) )
        return codeL
         

    ## Compile the code associated with one statement and return list of code for it.
    # @param self : Control_Function object
    # @param stmt : Pyparsing control_statement object
    # @param p4   : p4 object
    # @returns codeL : list of Strings implementing python code for this statement.
    def compile_stmt( self, stmt, p4 ):
        assert len(stmt)>1
        stmt_type = stmt[0]
        if stmt_type == 'if':
            return self.compile_if_stmt( stmt, p4)
        if stmt_type == 'apply_table':
            return self.compile_apply_table( stmt, p4)
        if stmt_type == 'do_ctrl_func':
            return self.compile_ctrl_func( stmt, p4)
        raise GP4_Exceptions.InternalError(
            'Unknown Control Function Statement Type in "%s": %s' % (self.name, stmt_type) )
        
       

    ## Compile the code associated with an IF statement and return list of code for it.
    # @param self : Control_Function object
    # @param stmt : Pyparsing control_statement object
    # @param p4   : p4 object
    # @returns codeL : list of Strings implementing python code for this statement.
    def compile_if_stmt( self, stmt, p4 ):
        assert len(stmt)>2  # must be at least 'if' <bool> <stmt>
        if_expr = stmt[1]
        then_expr = stmt[2]
        else_expr = stmt[3] if len(stmt) == 4 else None

        print "IF",if_expr,"THEN",then_expr,"ELSE",else_expr
        if_expr_code = flatten_list_of_strings(if_expr)
        print if_expr_code
        codeL = [ 'if '+if_expr_code+':' ]

        then_expr_codeL = self.generate_body_code( p4, then_expr )
        for stmt in then_expr_codeL:
            codeL.append( '   ' + stmt )

        if else_expr:
            else_expr_codeL = self.generate_body_code( p4, else_expr )
            codeL.append('else:')
            for stmt in else_expr_codeL:
                codeL.append( '   ' + stmt )

        return codeL
       

    ## Compile the code associated with an 'apply table' statement and return list of code for it.
    # @param self : Control_Function object
    # @param stmt : Pyparsing control_statement object
    # @param p4   : p4 object
    # @returns codeL : list of Strings implementing python code for this statement.
    def compile_apply_table( self, stmt, p4 ):
        assert len(stmt)>1  # must be at least 'apply_table' <table_name>
        table_name = stmt[1]
        if not p4.get_table(table_name):
            raise GP4_Exceptions.RuntimeError, \
                "Table '%s' unknown." % table_name
        return [ 'p4.get_table("%s").apply(p4)' % table_name ]
        

    ## Compile the code associated with a 'do ctrl function' statement and return list of code for it.
    # @param self : Control_Function object
    # @param stmt : Pyparsing control_statement object
    # @param p4   : p4 object
    # @returns codeL : list of Strings implementing python code for this statement.
    def compile_ctrl_func( self, stmt, p4 ):
        assert len(stmt)>1  # must be at least 'do_ctrl_func' <func_name>
        func_name = stmt[1]
        if not p4.get_control_function(func_name):
            raise GP4_Exceptions.RuntimeError, \
                "Ctrl function '%s' unknown." % func_name
        return [ 'p4.get_control_function("%s").execute(p4)' % func_name ]
       

    def __str__(self):
        s = self.name + '()'
        return s
