# GP4_Header_Stack.py.  Stack of Header Instances
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_Header_Instance import Header_Instance

class Header_Stack(Header_Instance):

    ## Construct new Header_Stack object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param hdr_type_name    : String. Name of the header decl that this is an instance of.
    # @param hdr_is_metadata  : Bool 
    # @param hdr_inst_name    : String. Name of this instance.
    # @param hdr_max_inst_val : Integer.  Maximum number of instances in array (stack)
    # @returns self
    def __init__(self, string, loc, 
                hdr_type_name, hdr_is_metadata, hdr_inst_name, hdr_max_inst_val=1):
        
        super(Header_Stack, self).__init__(string, loc, 
                                           hdr_type_name, 
                                           hdr_is_metadata, 
                                           hdr_inst_name)
        self.typ = 'header_stack'

        # Sub classed:
        # self.hdr_type_name    = hdr_type_name
        # self.hdr_is_metadata  = hdr_is_metadata
        # self.hdr_inst_name    = hdr_inst_name

        self.stack_max_size = hdr_max_inst_val # Integer. How many instances can we hold
        self.stack          = [ ] # [ Header_Instance objects ]
        self.stack_depth    = 0   # number of instances created in stack[]

    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        s += ' [1..' + str(self.stack_depth) + ']' if self.stack_depth else '[empty]'
        s += ' (max=%d)' % self.stack_max_size
        return s
