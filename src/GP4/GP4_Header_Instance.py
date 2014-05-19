# GP4_Header_Instance.py Header Instance Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object
import GP4_Exceptions

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

        self.fields_created = False   # Bool. Set when fields are actually created (extracted)
        self.fields         = []      # ordered list of Field objects
        self.field_names    = []      # ordered list of field names
        self.compute_length = None    # Function to compute length of header. Built at run time.


    ## Instantiate the actual fields from the header_decl
    # @param self : object
    # @returns err String: '' is no error
    def create_fields(self, p4): 

        decl = p4.get_header_decl(self.hdr_type_name)
        if not decl:
            return('Unknown header declaration "%s" referenced by header instance "%s"' %
                    (self.hdr_type_name, self.hdr_inst_name) )

        self.fields         = decl.copy_fields()
        self.field_names    = [ f.name for f in self.fields ]
        self.fields_created = True

        print "Created fields for",self.hdr_inst_name
        return ''

    ## Return bool indicating if specified field name is valid (has value)
    # @param self : object
    # @param String: field_name
    # @returns Bool
    def field_has_value(self, field_name):
        for f in self.fields:
            if f.name == field_name: return f.is_valid
        return False



    ## Set field to given value
    # @param self : object
    # @param field_name : String
    # @param val : Integer
    # @return None    
    def set_field(self, field_name, val): 

        for ix,fname in enumerate(self.field_names):
            if fname == field_name:
                self.fields[ix].set_value( val )
                print "set %s.%s to %s" % (self.hdr_inst_name, field_name, val)
                return
                
        assert False,"set_field: Unknown field name %s" % field_name



    ## Get value of field
    # @param self : object
    # @param field_name : String
    # @return val : Integer
    def get_field(self, field_name): 

        for ix,fname in enumerate(self.field_names):
            if fname == field_name:
                return self.fields[ix].get_value()

        return None

    ## Get bit width of field
    # @param self : object
    # @param field_name : String
    # @return val : Integer
    def get_field_width(self, field_name): 

        for ix,fname in enumerate(self.field_names):
            if fname == field_name:
                return self.fields[ix].get_actual_width()

        return 0



    ## Compute 'length' expression for this hdr. Return how many bits not already extracted.
    # @param self : object
    # @param p4   : P4 object
    # @return val : Integer
    def compute_remaining_header_length_bits(self, p4):
        print "compute_remaining_header_length"
        if not self.compute_length:
            self.compile_compute_length(p4)
        length = 8 * self.compute_length(self, p4)
        print "compute_length returned length of ",length

        current_length = self.compute_current_bit_length()

        # If max_length was specified then check it.
        decl = p4.get_header_decl(self.hdr_type_name)
        if not decl:
            raise GP4_Exceptions.RuntimeError, \
            'Unknown header declaration "%s" referenced by header instance "%s"' % \
                    (self.hdr_type_name, self.hdr_inst_name) 
        if decl.max_length:
            if current_length > (8*decl.max_length):
                raise GP4_Exceptions.RuntimeParseError, \
                    "Header %s: max_length of %d exceeded: already extracted %d bytes." % \
                        ( self.hdr_inst_name,  decl.max_length, current_length/8 )

        if current_length >= length: return 0
        return length - current_length



    ## Compile the 'length' expression for this hdr
    # @param self : object
    # @param p4   : P4 object
    # @return None
    def compile_compute_length(self, p4):
        """ Get the length expression from the hdr decl, and build a python
            function from it.
        """
        decl = p4.get_header_decl(self.hdr_type_name)
        if not decl:
            raise GP4_Exceptions.RuntimeError, \
            'Unknown header declaration "%s" referenced by header instance "%s"' % \
                    (self.hdr_type_name, self.hdr_inst_name) 
        len_expr = decl.get_flattened_length_expr()
        expr = len_expr.split()

        code = 'def f(self,p4): return ( '

        for atom in expr:
            if atom[0].isalpha() :  # field
                if not atom in self.field_names:
                    raise GP4_Exceptions.SyntaxError, \
                        "Error: Hdr_decl %s: length expression uses field '%s' which is not in declaration"%\
                        (decl.name, atom)
                code += 'self.get_field("%s")' % atom
            else: # value of operator
                if atom[0].isdigit():
                    code += atom
                else:
                    code += ' ' + atom + ' '
        code += ' )'
    
        print "code is:",code

        # Now compile the code
        try:
            exec code
        except Exception as ex_err:
            print "Error: generated code for python function yielded exception:",ex_err.data
            print "code was <\n",code,"\n>\n"
            raise GP4_Exceptions.RuntimeError, ex_err.data
                

        self.compute_length = f  # f is the function we just created
        return


    ## Compute the length (bits) of all headers already extracted.
    # @param self : object
    # @return val : Integer
    def compute_current_bit_length(self):
        return sum([f.valid_bits for f in self.fields])


    ## Return the name of the declaration for this instance
    # @param self : object
    # @returns String
    def get_decl_name(self):
        return self.hdr_type_name


    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        if self.fields_created:
            s += '\n'
            for f in self.fields: s += '   ' + str(f) + '\n'
        return s
