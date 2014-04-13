# GP4_Compile.py : P4 compiler class
# Given a parse tree, compile it.
#
## @package GP4

import GP4_P4
#from GP4_Exceptions import *
#from GP4_PyParse import *

class Compiler(object):

    def __init__(self):
        pass



    ## Compile a P4 program given as a single string.
    # @param self: Compiler object
    # @param parse_tree : the list of AST object created by PyParsing lib.
    # @return p4 object or None if error
    def compile_parse_tree(self, parse_tree):

        # print "parse tree is ", parse_tree
        p4 = GP4_P4.P4()

        for ast_obj in parse_tree:
            p4.add_AST_obj( ast_obj )

        return p4
