# GP4_Deparser.py : P4 Deparser Object
#
## @package GP4

from GP4_Utilities  import *
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

class Deparser(AST_object):

    ## Construct new Deparser object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the Deparser
    # @param refs   : [ hdr_refs or field_refs ] (PyParsing objects)
    # @returns self
    def __init__(self, string, loc, name, refs = [] ):
        
        super(Deparser, self).__init__(string, loc, 'deparser')

        self.name  = name
        self.refs  = refs


    ## convert to string
    # @param self : deparser object
    # returns string
    def __str__(self):
        s = self.name
        for h in self.refs:
            s += ' ' + str(h)
        return s
