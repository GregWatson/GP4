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

    def __str__(self):
        s = self.name + ':' + str(self.bit_width) 
        if len(self.modifiers):
            s += '('+ ','.join(self.modifiers) + ')'
        return s
