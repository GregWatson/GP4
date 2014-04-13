# GP4_Header_Instance.py Header Instance Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object

class Header_Instance(AST_object):

    ## Construct new Header_Instance object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param hdr_type_name   : String. Name of the header decl that this is an instance of.
    # @param hdr_is_metadata : Bool 
    # @param hdr_inst_name   : String. Name of this instance.
    # @returns self
    def __init__(self, string, loc, 
                hdr_type_name, hdr_is_metadata, hdr_inst_name):
        
        super(Header_Instance, self).__init__(string, loc, 'header_instance')

        self.hdr_type_name    = hdr_type_name    # name of hdr decl that this instantiates
        self.hdr_is_metadata  = hdr_is_metadata  # Bool.
        self.hdr_inst_name    = hdr_inst_name    # name of this instance

        self.is_valid = False   # Bool. Set when actually created (extracted)



    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        return s
