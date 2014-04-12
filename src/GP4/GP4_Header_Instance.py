# Header Instance Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object

class Header_Instance(AST_object):

    ## Construct new Header_Instance object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param hdr_type_name : String. Name of the header decl that this is an instance of.
    # @param hdr_is_metadata : Bool 
    # @param hdr_inst_name : String. Name of this instance.
    # @param hdr_is_array : Bool.  If array then hdr_max_inst_val is valid
    # @param hdr_max_inst_val : Integer.  Maximum number of instances in array (stack)
    # @returns self
    def __init__(self, string, loc, 
                hdr_type_name, hdr_is_metadata, hdr_inst_name, hdr_is_array, hdr_max_inst_val=1):
        
        super(Header_Instance, self).__init__(string, loc, 'header_instance')

        self.hdr_type_name    = hdr_type_name
        self.hdr_is_metadata  = hdr_is_metadata
        self.hdr_inst_name    = hdr_inst_name
        self.hdr_is_array     = hdr_is_array
        self.hdr_max_inst_val = hdr_max_inst_val



    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        s += ' [1..' + str(self.hdr_max_inst_val) + ']' if  self.hdr_is_array else ''
        return s
