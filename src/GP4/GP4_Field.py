# GP4_Field.py
# Field Object.  Used for both Field Declarations and Instances.
#
## @package GP4

from GP4_AST_object import AST_object

class Field(AST_object):

    ## Construct new Field object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param fld_name  : String. Name of the Field declaration .e.g offset
    # @param fld_width : Integer. Width of field in bits or 0 if '*' (undefined)
    # @param fld_mods : List of optional modifier strings
    # @returns self
    def __init__(self, string, loc, fld_name , fld_width, fld_mods ):

        super(Field, self).__init__(string, loc, 'field')

        self.name      = fld_name   # String
        self.bit_width = fld_width  # Integer.  0 means variable length ('*')
        self.modifiers = fld_mods   # [ String ] : 'saturating', 'signed'

        # following used by field instances.
        self.is_valid = False  
        self.value    = None   # Integer
        self.valid_bits = 0    # number of bits when is_valid


    ## Assign a value
    # @param self  : object
    # @param value : Integer. New value for this field.
    # @param num_bits : Integer. Number of bits to associate with value. If None: use bit_width
    # @returns None
    def set_value(self, value, num_bits=None):
        self.value    = value
        self.is_valid = True
        self.valid_bits = num_bits if num_bits != None else self.bit_width


    ## Return value
    # @param self  : object
    # @returns value : Integer. Value for this field.
    def get_value(self):
        if self.is_valid: return self.value
        else: return None


    ## Return actual bit width (not declared width)
    # @param self  : object
    # @returns width : Integer. width of this field.
    def get_actual_width(self):
        if self.is_valid: return self.valid_bits
        else: return 0


    ## Convert field to a printable string
    # @param self  : object
    # @returns String representing field
    def __str__(self):
        s = self.name + ':' + str(self.bit_width) 
        s+= " val=0x%x " % self.value if self.is_valid else " <undef>"
        if len(self.modifiers):
            s += '('+ ','.join(self.modifiers) + ')'
        return s
