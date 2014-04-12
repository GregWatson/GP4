# Header Declaration Object
#
## @package GP4

from GP4_CompilerHelp import print_syntax_err

class Header_Declaration(object):

    ## Construct new Header_Declaration object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param hdr_name : String. Name of the header declaration .e.g ip
    # @param hdr_body : 
    # @parblock
    #           List of 1,2, or 3 object. 1st is [ field_dec ]. 
    #           Others are 'length' or 'max_length'
    # @endparblock
    # @returns self
    def __init__(self, string, loc, hdr_name , hdr_body ):

        print "Constructing header",hdr_name

        assert len(hdr_body)>0 and len(hdr_body)<4

        self.name        = hdr_name
        self.fields      = hdr_body[0]  # must be present
        self.field_names = []
        self.length_expr = None
        self.max_length  = 0
        
        hdr_len_undefined = False   # set if we see field with bit_width '*'   (0)
        for f in self.fields:
            if f.name in self.field_names:
                print_syntax_err('Field name "%s" already defined in header "%s"' %
                                (f.name, self.name), string, loc)

            if f.bit_width == 0:
                if hdr_len_undefined:
                    print_syntax_err('In header "%s" two or more fields have undefined width.' %
                                     self.name, string, loc)
                
                hdr_len_undefined = True 


            self.field_names.append(f.name)

        # Process options

        if len(hdr_body)>1:
            for opt in hdr_body[1:]: 
                print "  opt:", opt
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
                
        

