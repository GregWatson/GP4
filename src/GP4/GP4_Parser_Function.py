# GP4_Parser_Function.py : Parser function Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

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
    # @returns (err, bytes_used, next_state)
    def execute(self, p4, bits):

        # If we have not yet compiled the function then do so in context of the P4 object
        if not self.func: 
            err = self.compile_func(p4)
            if err: return(err,0,self.name)

        return self.func(self, p4, bits)

    ## Compile the function in the context of a P4 object (namespace)
    # @param self : object
    # @param p4   : P4 object
    # @returns err
    def compile_func(self, p4):
        """ The actual compiled code has signature:
            (err, bytes_used, state) = func( p4, bits)

            Each statement should return (err, bytes_used, state)
            where bytes_used is bytes used by that statement.
        """
        err = None
        codeL = [ 
                  'def f(self, p4, bits):',
                  '    err = ""; total_bytes = 0; state=self.name',
                  '    print "executing func",self.name'
                ]

        for stmt in self.func_body_text: 
            # print "compiling stmt ", stmt
            err, code = self.compile_stmt(stmt, p4)
            codeL.append('    (err, bytes_used, state)=' + code)
            codeL.append('    total_bytes += bytes_used')
            codeL.append('    if err: return (err, total_bytes, state)' )
            if err: return (err, codeL)

        codeL.append('    return (err, total_bytes, state)')

        text = '\n'.join(codeL)
        print "Compiling code:\n",text

        try:
            exec text
        except Exception as e:
            print "Error: generated code for python function yielded exception:",e
            print "code was <\n",text,"\n>\n"
            raise GP4_Exceptions.RuntimeError,[e]

        self.func = f
        return err

    ## Compile a single statement and return the text for that statement as a string
    # @param self : object
    # @param stmt : PyParsing list of parsed objects.
    # @param p4   : P4 object
    # @returns (err, code) 
    def compile_stmt(self, stmt, p4):
        """    Each statement should return (err, bytes_used, state)
               where bytes_used is bytes used by that statement.
        """
        stmt_typ = 'compile_stmt_' + stmt[0]  # e.g. compile_stmt_extract

        if stmt_typ not in dir(self):
            print "Internal Error. compile_stmt: unknown statement type " + stmt_typ
            raise GP4_Exceptions.InternalError, ''

        (err, code) = getattr(self, stmt_typ)(stmt, p4)
        return (err,code)

    ## Compile an extract statement and return the compiled python text.
    # @param self : object
    # @param stmt : PyParsing list of parsed objects.
    # @param p4   : P4 object
    # @returns (err, code) 
    def compile_stmt_extract(self, stmt, p4):
        """Each statement should return (err, bytes_used, state)
           where bytes_used is bytes used by that statement.

           stmt is ['extract', 'L2_hdr'] or ['extract', 'L2_hdr', index] index= str(num) or 'next' 
        """
        assert len(stmt)>1
        hdr_name  = stmt[1]

        #check header inst exists
        if not p4.hdr_inst_defined(hdr_name):
            return ('Unknown header instance "%s".' % hdr_name, 'extract error')

        index = "''" if  len(stmt)<3 else stmt[2]

        code = 'p4.extract(p4.get_hdr_inst("' + hdr_name + '", ' + index + '), bits)'
        # print code
        return ('', code)


    ## Compile a return done statement and return the compiled python text.
    # @param self : object
    # @param stmt : PyParsing list of parsed objects.
    # @param p4   : P4 object
    # @returns (err, code) 
    def compile_stmt_return_done(self, stmt, p4):
        """Each statement should return (err, bytes_used, state)
           where bytes_used is bytes used by that statement.
        """
        code = '("", 0, "P4_PARSING_DONE")'
        return ('', code)


    ## Compile a 'return next_state' statement and return the compiled python text.
    # @param self : object
    # @param stmt : PyParsing list of parsed objects.
    # @param p4   : P4 object
    # @returns (err, code) 
    def compile_stmt_return_prsr_state(self, stmt, p4):
        """Each statement should return (err, bytes_used, state)
           where bytes_used is bytes used by that statement.

           stmt is ['return_prsr_state', 'DO_L9']
        """
        code = '("", 0, "' + stmt[1] + '")'
        return ('', code)




    def __str__(self):
        s = self.name + '()'
        return s
