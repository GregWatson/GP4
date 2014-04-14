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

        self.is_valid = False   # Bool. Set when fields are actually created (extracted)
        self.fields = []        # ordered list of Field objects
        self.field_names = []   # ordered list of field names

    ## Instantiate the actual fields from the header_decl
    # @param self : object
    # @returns err String: '' is no error
    def create_fields(self, p4): 

        decl = p4.get_header_decl(self.hdr_type_name)
        if not decl:
            return('Unknown header declaration "%s" referenced by header instance "%s"' %
                    (self.hdr_type_name, self.hdr_inst_name) )

        self.fields      = decl.copy_fields()
        self.field_names = [ f.name for f in self.fields ]


    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        return s
