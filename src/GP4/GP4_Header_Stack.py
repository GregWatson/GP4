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
        """ Assume instances start at 0 (innermost) and increment
        """
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


    ## Return bool if stack index is in range (legal). Entry need not exist yet.
    # @param self : object
    # @param index : number or string 'next' or string 'last'
    # @return Bool
    def is_legal_index(self, index):
        if index == 'last': return True
        if index == 'next':
            return len(self.stack) < self.stack_max_size
        return int(index) < self.stack_max_size
    

    ## Return the specified (indexed) instance. Create it if needed.
    # @param self : object
    # @param index : number or string 'next' or string 'last'
    # @return actual header instance. Create instance if needed.  None if error
    def get_or_create_indexed_instance(self, index):
        """ index may be a number or 'next'.
            Create instance if it does not exist, IF it is the next to be created.
        """
        # Create a new header_inst if index is next or else it is a value equal to
        # the next index to be used in the stack.
        if index == 'next' or index == len(self.stack):
            if len(self.stack) == self.stack_max_size:  # full - return None
                print "Referenced instance",index,"of stack %s but stack is full." % self.hdr_inst_name
                return None
            # Create new header instance
            #print "Creating hdr inst %s[%d]" % (self.hdr_inst_name, len(self.stack))
            h_i = Header_Instance(  self.string, self.loc,
                                    self.hdr_type_name,
                                    self.hdr_is_metadata,
                                    "%s[%d]" % (self.hdr_inst_name, len(self.stack))
                                  )
            self.stack.append(h_i)
            return h_i

        if index == 'last':
            if len(self.stack) == 0:
                print "Referenced 'last' hdr_inst of stack %s but stack is empty." % self.hdr_inst_name
                return None
            return self.stack[-1]

        # Get actual numbered entry
        if index >= len(self.stack):
            print "Indexed entry %d of stack %s but stack only has %d entries." % (
                    index, self.hdr_inst_name, len(self.stack) )
            return None
        return self.stack[index]





    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        s += ' [0..' + str(self.stack_depth) + ']' if len(self.stack) else '[empty]'
        s += ' (max=%d)' % self.stack_max_size
        return s
