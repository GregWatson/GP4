# GP4 Compiler Helper functions
#
## @package GP4

import GP4_Compile, GP4_PyParse
from GP4_Utilities import *
from pyparsing import ParseException
import GP4_Exceptions

## Compile a GP4 program given as a single string.
# @param program : string. The GP4 program
# @param debug : debug vector integer
# @return p4 object or None if error
def compile_string(program, debug=0, ):
    ''' Creates a new parser and compiler object.
        Runs the parser on the given program, and then
        runs the compiler on the generated AST, 
        returning a P4 object that contains the 
        specified P4 program.
    '''

    if debug:
        print program

    parser = GP4_PyParse.new_GP4_parser()

    try:
        parsed_data = parser.parseString(program, True)

    except ParseException as err:

        show_source_loc(err.line, err.column)
        print err
        raise GP4_Exceptions.SyntaxError, err

    # Compile the parse tree

    compiler = GP4_Compile.Compiler( )
    p4 = compiler.compile_parse_tree( parsed_data )

    return p4




