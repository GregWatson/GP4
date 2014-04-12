# Field Declaration Object

from GP4_AST_object import AST_object

class Field_Declaration(AST_object):

    ## Construct new Field_Declaration object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param fld_name  : String. Name of the Field declaration .e.g offset
    # @param fld_width : Integer. Width of field in bits or 0 if '*' (undefined)
    # @param fld_mods : List of optional modifier strings
    # @returns self
    def __init__(self, string, loc, fld_name , fld_width, fld_mods ):

        super(Field_Declaration, self).__init__(string, loc, 'field_declaration')

        self.name      = fld_name
        self.bit_width = fld_width
        self.modifiers = fld_mods
        # print self

    def __str__(self):
        s = self.name + ':' + str(self.bit_width) 
        if len(self.modifiers):
            s += '('+ ','.join(self.modifiers) + ')'
        return s
