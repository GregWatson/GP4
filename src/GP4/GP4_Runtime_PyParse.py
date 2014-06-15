# GP4_Runtime_PyParse: BNF definitions for runtime cmds
#
## @package GP4

from pyparsing import *
import sys

ParserElement.enablePackrat()  # REALLY helps performance of operatorPrecedence()

## Construct a new Runtime_PyParsing Parser
# @return parser object.
def new_GP4_runtime_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK, LBRACE, RBRACE = map(Suppress, '()[]{}')
    SEMICOLON, COLON, COMMA =  map(Suppress, ';:,')
    
    # --- General ---------------------------------------------

    action_name      = Word(alphas,alphanums+'_')
    field_name       = Word(alphas,alphanums+'_')
    header_type_name = Word(alphas,alphanums+'_')
    instance_name    = Word(alphas,alphanums+'_')
    decimalnum       = Word(nums+'-',nums)
    hexnum           = Combine(Literal('0x') + Word(hexnums) )
    value            = hexnum | decimalnum 

    # --- Header and Field references ---------------------

    index = ( value | Literal('Last') )

    header_ref = Group ( 
                           ( instance_name + LBRACK + index + RBRACK ) 
                         |   instance_name 
                       )

    field_ref  = Group ( header_ref + Suppress('.') + field_name )

    # --- Action definition ---------------------------------

    param_name = Word(alphas,alphanums+'_')

    arg = value | field_ref | header_ref | param_name # counter_ref | meter_ref 

    action_statement = Group(action_name + LPAREN + delimitedList(arg) + RPAREN )

    # --- Table Operations ------------------------------------

    table_name   = Word(alphas,alphanums+'_')

    # e.g. my_table.set_default_action( add_to_field ( hop_count_hdr.count, 1 ))

    table_set_default_action = Group(  Combine( table_name + Literal('.set_default_action') )
                                      + LPAREN + action_statement + RPAREN
                                    )

    table_op = table_set_default_action.copy()
    table_op.setParseAction( table_op_action )


    # --- Runtime Cmds  ------------------------------------

    runtime_cmd = (  table_op
                  )

    parser = OneOrMore(runtime_cmd)
    parser.ignore(cStyleComment)

    # parser.validate( ) # check recursive or not
    # parser.setDebug( ) # print debug info while parsing source text

    return parser

####################################################
# parser Actions

## Modify the parse tree for a table operation (method call on a table)
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def table_op_action (string, loc, toks):
    """ input is like    [ table_name.method [ args ] ]
        change it to:    [ 'table_op', table_name , method, [ args ] ]
    """
    cmd = toks[0].asList()
    tbl_name, tbl_method = cmd[0].split('.')
    hdr = [ 'table_op', tbl_name, tbl_method ]
    hdr.extend(cmd[1:])
    toks[0] = hdr


####################################################
if __name__ == '__main__' :

    txt = 'length (2+3*fred+2) ;'
    parser = new_GP4_parser()
    print txt
    parsed_data = parser.parseString(txt, True)
    print parsed_data

