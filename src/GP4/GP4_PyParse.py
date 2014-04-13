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
    SEMICOLON, COLON, COMMA =  map(Suppress, ';:,')
    
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

    # --- Header and Field references ---------------------

    index = ( value | Literal('Last') )

    header_ref = Group (    instance_name 
                         | ( instance_name + LBRACK + index + RBRACK ) 
                       )

    field_ref  = Group ( header_ref + Suppress('.') + field_name )

    # --- Parser Functions --------------------------------

    parser_state_name = Word(alphas,alphanums+'_')
    mask_value        = Word(nums)

    switch_field_ref = Group (   field_ref 
                               | ( Literal('latest.') + field_name ) 
                               | (   Literal('current') 
                                   + LPAREN + value + COMMA + value + RPAREN )
                             )

    switch_exp = Group ( delimitedList( switch_field_ref ) )

    value_or_masked = Group ( ( value + Suppress('mask') + mask_value ) | value )

    value_list = Group ( delimitedList( value_or_masked ) | Literal('default') )

    case_entry = Group ( value_list + COLON +  parser_state_name + SEMICOLON )

    return_stmt_P4_done = Group (  Suppress('return') + Suppress('P4_PARSING_DONE') 
                                 + SEMICOLON )

    return_stmt_prsr_st_name = Group ( Suppress('return') + parser_state_name + SEMICOLON )

    return_stmt_switch = Group (   Suppress('return') + Suppress('switch') 
                                 + LPAREN + switch_exp + RPAREN
                                 + LBRACE + OneOrMore( case_entry ) + RBRACE
                               )

    return_statement = (   return_stmt_P4_done 
                         | return_stmt_prsr_st_name
                         | return_stmt_switch 
                       )


    set_statement = Group (   Literal('set_metadata') 
                            + LPAREN + field_ref + COMMA + value + RPAREN 
                            + SEMICOLON 
                          )

    header_extract_index = ( value | Literal('next') )

    header_extract_ref = (   ( instance_name + LBRACK + header_extract_index + RBRACK )
                           | instance_name 
                         )

    extract_statement = Group (   Literal('extract') 
                                + LPAREN + header_extract_ref + RPAREN + SEMICOLON
                              )

    extract_or_set_statement = ( extract_statement | set_statement )

    parser_function_body = Group (   ZeroOrMore ( extract_or_set_statement )
                                   + return_statement
                                 )

    parser_function = Group (   Suppress('parser')
                              + parser_state_name 
                              + LBRACE + parser_function_body + RBRACE )

    return_stmt_P4_done.setParseAction     (lambda t: [[ 'return_done' ]] )
    return_stmt_prsr_st_name.setParseAction(lambda t: t[0].insert(0,'return_prsr_state') )
    return_stmt_switch.setParseAction      (lambda t: t[0].insert(0,'return_switch') )

    # --- P4 definition ------------------------------------

    p4_declaration = (   header_declaration 
                       | instance_declaration 
                       | parser_function 
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

