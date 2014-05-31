# GP4_Table.py : P4 Table Object
#
## @package GP4

from GP4_Utilities  import *
#from GP4_Parser_Function_Code import *
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

class Table(AST_object):

    ## Construct new Table object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the Table
    # @param field_matches : List of Pyparsing field_match objects
    # @param actions  : List of Pyparsing action_next_table objects
    # @param min_size : Integer. 
    # @param max_size : Integer. 
    # @returns self
    def __init__(self, string, loc, name, field_matches=[], actions=[], 
                                          min_size=None, max_size=None ):
        
        super(Table, self).__init__(string, loc, 'table')

        self.name          = name
        self.field_matches = field_matches
        self.actions       = actions
        self.min_size      = min_size
        self.max_size      = max_size


    ## Apply this table with a P4 argument as context.
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @returns None
    def apply( self, p4 ):
        print "Applying table",
        print str(self)

       

    def __str__(self):
        s = self.name + '()\n'
        if len(self.field_matches):
            s+='   Field matches:'
            for el in self.field_matches:
                s += str(el) + ';'
            s+='\n'
        if len(self.actions):
            s+='   Actions:'
            for el in self.actions:
                s += str(el) + ';'
            s+='\n'

        return s
