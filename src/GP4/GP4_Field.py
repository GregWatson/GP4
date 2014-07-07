# GP4_Field.py
# Field Object.  Used for both Field Declarations and Instances.
#
## @package GP4

from GP4_AST_object import AST_object
from GP4_Utilities  import *

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


    ## Make a copy of self
    # @param self  : object
    # @returns New Field object
    def copy(self):
        new = Field(self.string, self.loc, self.name, self.bit_width, self.modifiers)
        new.is_valid   = self.is_valid
        new.value      = self.value
        new.valid_bits = self.valid_bits
        return new


    ## Assign a value
    # @param self  : object
    # @param value : Integer. New value for this field.
    # @param num_bits : Integer. Number of bits to associate with value. If None: use bit_width
    # @returns None
    def set_value(self, value, num_bits=None):
        self.valid_bits = num_bits if num_bits != None else self.bit_width
        mask = (1<<self.valid_bits)-1  
        self.value    = value & mask
        self.is_valid = True

    ## Assign a value in a non-blocking way - does not change the actual value until p4 update()'s it.
    # @param self  : object
    # @param p4    : P4 object
    # @param value : Integer. New value for this field.
    # @param num_bits : Integer. Number of bits to associate with value. If None: use bit_width
    # @returns None
    def set_non_blocking_value(self, p4, value, num_bits=None):
        self.valid_bits = num_bits if num_bits != None else self.bit_width
        mask = (1<<self.valid_bits)-1  
        self.non_blocking_value  = value & mask
        self.is_valid = True
        p4.add_modified_field(self)


    ## Update the field's value from its non-blocking value.
    # @param self  : object
    # @returns None
    def update_value(self):
        self.value    = self.non_blocking_value
        self.is_valid = True


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


    ## Create a Match_Key from self.
    # @param self  : object
    # @returns Match_Key
    def make_Match_Key(self, mk_type):
        mk = Match_Key(value=self.value, length=self.valid_bits, valid=self.is_valid)
        return mk

    ## Convert field to a printable string
    # @param self  : object
    # @returns String representing field
    def __str__(self):
        s = self.name + ':' + str(self.bit_width) 
        s+= " val=0x%x " % self.value if self.is_valid else " <undef>"
        if len(self.modifiers):
            s += '('+ ','.join(self.modifiers) + ')'
        return s
