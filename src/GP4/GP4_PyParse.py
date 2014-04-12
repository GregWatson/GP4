# GP4 PyParsing BNF definitions.
#
## @package GP4

from pyparsing import *
from GP4_PyParse_Actions import *
import sys



## Construct a new PyParsing Parser for P4
# @return parser object.
def new_GP4_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK, LBRACE, RBRACE = map(Suppress, '()[]{}')
    SEMICOLON, COLON =  map(Suppress, ';:')
    
    # --- Header declaration ----------------------------

    field_name       = Word(alphas,alphanums+'_')
    header_type_name = Word(alphas,alphanums+'_')
    value            = Word(nums)
    bit_width        = value | Literal("*")

    multOp   = Literal('*')
    plusOp   = oneOf('+ -')
    shiftOp  = oneOf('<< >>')

    atom  = value | field_name

    length_exp = operatorPrecedence( atom,
                            [
                             (shiftOp, 2, opAssoc.LEFT),
                             (multOp,  2, opAssoc.LEFT),
                             (plusOp,  2, opAssoc.LEFT),
                            ] )

    field_mod = Literal('signed') | Literal('saturating')

    field_mod_list = Group ( delimitedList(field_mod) )

    field_dec = Group (  field_name + COLON + bit_width 
                       + Optional( field_mod_list ) 
                       + SEMICOLON 
                      )

    hdr_length_option     = Group ( Literal('length')     + length_exp + SEMICOLON ) 
    hdr_max_length_option = Group ( Literal('max_length') + value      + SEMICOLON  )

    header_dec_body = Group (   Suppress('fields') 
                              + LBRACE + Group ( OneOrMore ( field_dec ) ) + RBRACE
                              + Optional( hdr_length_option )
                              + Optional( hdr_max_length_option )
                            )

    header_declaration = Group (  Suppress ('header') 
                                + header_type_name 
                                + LBRACE + header_dec_body + RBRACE
                               )
    
    bit_width.setParseAction(  lambda t: 0 if t[0] == '*' else int(t[0]) )
    header_declaration.setParseAction( do_header_declaration )
    field_dec.setParseAction( do_field_declaration )
    field_mod_list.setParseAction( do_field_mod_list )


    # --- Header Instantiation ---------------------------

    instance_name      = Word(alphas,alphanums+'_')
    max_instance_value = Word(nums)

    scalar_instance    = Group (   header_type_name 
                                 + Optional(Literal('metadata'))
                                 + instance_name 
                                 + SEMICOLON
                                )

    array_instance   =  Group (   header_type_name 
                                + instance_name 
                                + LBRACK + max_instance_value + RBRACK 
                                + SEMICOLON
                              )

    instance_declaration = ( scalar_instance | array_instance )

    # array_instance.setParseAction( lambda t: sys.stdout.write("parsed array_instance\n") )
    instance_declaration.setParseAction( do_instance_declaration )

    # --- P4 definition ------------------------------------

    p4_declaration = (   header_declaration 
                       | instance_declaration 
                       # | parser_function 
                       # | action_function 
                       # | table_declaration 
                       # | control_function
                     )

    parser = OneOrMore(p4_declaration)
    parser.ignore(cStyleComment)

    # parser.validate( ) # check recursive or not
    # parser.setDebug( ) # print debug info while parsing source text

    return parser



####################################################
if __name__ == '__main__' :

    txt = 'length (2+3*fred+2) ;'
    parser = new_GP4_parser()
    print txt
    parsed_data = parser.parseString(txt, True)
    print parsed_data

