# GP4 PyParsing BNF definitions.
#
## @package GP4

from pyparsing import *
from GP4_PyParse_Actions import *
import sys

ParserElement.enablePackrat()  # REALLY helps performance of operatorPrecedence()

## Construct a new PyParsing Parser for P4
# @return parser object.
def new_GP4_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK, LBRACE, RBRACE = map(Suppress, '()[]{}')
    SEMICOLON, COLON, COMMA =  map(Suppress, ';:,')
    
    # --- Header declaration ----------------------------

    field_name       = Word(alphas,alphanums+'_')
    header_type_name = Word(alphas,alphanums+'_')
    decimalnum       = Word(nums)
    hexnum           = Combine(Literal('0x') + Word(hexnums) )
    value            = hexnum | decimalnum 
    bit_width        = value | Literal("*")

    multOp   = Literal('*')
    plusOp   = oneOf('+ -')
    shiftOp  = oneOf('<< >>')

    atom  = value | field_name

    length_exp = operatorPrecedence( atom,  # highest precedence first
                            [
                             (multOp,  2, opAssoc.LEFT),
                             (plusOp,  2, opAssoc.LEFT),
                             (shiftOp, 2, opAssoc.LEFT),
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
    
    bit_width.setParseAction(  do_bit_width )
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

    header_ref = Group ( 
                           ( instance_name + LBRACK + index + RBRACK ) 
                         |   instance_name 
                       )

    field_ref  = Group ( header_ref + Suppress('.') + field_name )

    # --- Parser Functions --------------------------------

    parser_state_name = Word(alphas,alphanums+'_')
    mask_value        = Word(nums)

    switch_field_ref = Group (  
                                 ( Literal('latest.') + field_name ) 
                               | (   Literal('current') 
                                   + LPAREN + value + COMMA + value + RPAREN )
                               | field_ref 
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

    parser_function.setParseAction ( do_parser_function )


    # --- Control function ------------------------------------

    control_fn_name = Word( alphas,alphanums+'_' )
    table_name      = Word( alphas,alphanums+'_' )

    get_field_ref = field_ref.copy()
    get_field_ref.setParseAction( do_get_field_ref )

    unOp       = oneOf('~ -')
    binOp_and  = Literal('&')
    binOp_xor  = Literal('^')
    binOp_or   = Literal('|')

    exp_atom  = value | get_field_ref | oneOf('True False')

    exp = operatorPrecedence( exp_atom,    # highest precedence first
                            [
                             (unOp,       1, opAssoc.RIGHT),
                             (multOp,     2, opAssoc.LEFT),
                             (plusOp,     2, opAssoc.LEFT),
                             (shiftOp,    2, opAssoc.LEFT),
                             (binOp_and,  2, opAssoc.LEFT),
                             (binOp_xor,  2, opAssoc.LEFT),
                             (binOp_or,   2, opAssoc.LEFT),
                            ] )

    valid_header_ref = Suppress('valid') + LPAREN + header_ref + RPAREN
    valid_header_ref.setParseAction( do_valid_header_ref )

    relOp      = oneOf('> >= == <= < !=')
    exp_rel_op = Group( exp + relOp + exp )

    bool_expr_atom = valid_header_ref | exp_rel_op | exp

    boolOp_not = Literal('not')
    boolOp_and = Literal('and')
    boolOp_or  = Literal('or')

    bool_expr  = operatorPrecedence( bool_expr_atom, # highest precedence first
        [
            ( boolOp_not,  1, opAssoc.RIGHT),
            ( boolOp_and,  2, opAssoc.LEFT),
            ( boolOp_or,   2, opAssoc.LEFT),
        ] )

    control_statement = Forward()

    else_statement = Suppress('else') + LBRACE + Group ( OneOrMore( control_statement ) ) + RBRACE

    if_else_statement = Group ( Literal('if') + LPAREN + Group(bool_expr) + RPAREN
                                + LBRACE + Group ( OneOrMore( control_statement ) ) + RBRACE
                                + Optional(else_statement) )
    
    apply_table_statement = Group (  Literal('apply_table') 
                                   + LPAREN + table_name + RPAREN + SEMICOLON
                                  )

    apply_control_function_statement = Group ( control_fn_name +   LPAREN + RPAREN + SEMICOLON )
    apply_control_function_statement.setParseAction( do_apply_control_function_statement )

    control_statement << (   if_else_statement 
                           | apply_table_statement 
                           | apply_control_function_statement
                         )
    
    control_function = Group (   Suppress('control')
                               + control_fn_name
                               + LBRACE + Group ( OneOrMore( control_statement ) ) + RBRACE
                             )

    control_function.setParseAction( do_control_function )

    # --- Table definition ---------------------------------

    table_min_size = Group( Keyword('min_size') + value + SEMICOLON )
    table_max_size = Group( Keyword('max_size') + value + SEMICOLON )

    table_declaration = Group ( Suppress('table') + table_name + LBRACE 
                                + Optional( table_min_size )
                                + Optional( table_max_size )
                                + RBRACE )
    table_declaration.setParseAction( do_table_declaration )


#
#table-declaration ::=
#    table table-name {
#        [ reads { field-match + } ]
#        action-specification
#        [ min_size value ; ]
#        [ max_size value ; ]
#    }
#
#field-match ::= field-or-masked-ref : field-match-type ;
#field-or-masked-ref ::= field-ref | field-ref mask value
#field-match-type ::= exact | ternary | lpm | range | valid
#
#action-specification ::= 
#    actions { [ action-name  [ next_table table-name ] ; ] + }
#


    # --- P4 definition ------------------------------------

    p4_declaration = (   header_declaration 
                       | instance_declaration 
                       | parser_function 
                       # | action_function 
                       | table_declaration 
                       | control_function
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

