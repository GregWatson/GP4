# GP4_AST_object.py : Generic AST object created by parser
#
## @package GP4

from GP4_Utilities  import print_syntax_err

class AST_object(object):

    ## Construct new Header_Declaration object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param typ_name : String. Name of this object type
    # @returns self
    def __init__(self, string, loc, typ_name ):

        self.typ    = typ_name  # The specific AST object type (string)
        self.string = string    # actual source string (text) where defined
        self.loc    = loc       # position in text where defined
