# Header Declaration Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object
import copy

class Header_Declaration(AST_object):

    ## Construct new Header_Declaration object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param hdr_name : String. Name of the header declaration .e.g ip
    # @param hdr_body : 
    # @parblock
    #           List of 1,2, or 3 object. 1st is [ field_dec objects ]. 
    #           Others are 'length' or 'max_length'
    # @endparblock
    # @returns self
    def __init__(self, string, loc, hdr_name , hdr_body ):

        assert len(hdr_body)>0 and len(hdr_body)<4
        
        super(Header_Declaration, self).__init__(string, loc, 'header_declaration')

        self.name        = hdr_name
        self.fields      = hdr_body[0]  # [ Field objects ]
        self.field_names = []           # ordered list of field names
        self.length_expr = None         # list of strings. expression to calc length.
        self.max_length  = 0            # Integer. max length for header
        
        hdr_len_undefined = False       # True if we see a field with bit_width '*'   (0)
        bit_count = 0
        for f in self.fields:
            if f.name in self.field_names:
                print_syntax_err('Field name "%s" already defined in header "%s"' %
                                (f.name, self.name), string, loc)

            if f.bit_width == 0:
                if hdr_len_undefined:
                    print_syntax_err('In header "%s" two or more fields have undefined width.' %
                                     self.name, string, loc)
                
                hdr_len_undefined = True 

            bit_count += f.bit_width

            self.field_names.append(f.name)

        if ( bit_count % 8 ) != 0:
            if not hdr_len_undefined:
                print_syntax_err('In header "%s" total field bit_width not byte aligned: %d bits.' %
                                     (self.name, bit_count), string, loc)



        # Process options

        if len(hdr_body)>1:
            for opt in hdr_body[1:]: 
                # print "  opt:", opt
                assert len(opt)>1  # [0]=opt name, [1] = value
                opt_name = opt[0]
                if opt_name == 'length':
                    self.length_expr = opt[1]
                if opt_name == 'max_length':
                    self.max_length = int(opt[1])

        if hdr_len_undefined:
            if not  self.length_expr:
                 print_syntax_err('In header "%s" a field has width "*" so "length" must be defined.' %
                                     self.name, string, loc)

    ## Copy the actual field objects and return list of them
    # @param self : object
    # @returns new ordered list of field objects
    def copy_fields():
        return [ copy.deepcopy(f) for f in self.fields ]



    def __str__(self):
        s = self.name + ' {\n'
        for f in self.fields: s += '\t' + str(f) + '\n'
        if self.length_expr:
            s += "length = " + str(self.length_expr) + '\n'
        if self.max_length:
            s += "max_length = %d\n" % self.max_length
        s += '}'
        return s
