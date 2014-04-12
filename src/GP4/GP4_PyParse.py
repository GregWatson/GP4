# GP4 PyParsing BNF definitions.
#
## @package GP4

from pyparsing import *
import GP4_Header_Declaration
import GP4_Field_Declaration
from GP4_CompilerHelp import *




## construct a field modifier list (check valid)
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param string : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_field_mod_list(string, loc, toks):
    # print "field_mod_list:",toks[0]
    mods = toks[0]
    seen = []
    for m in mods:
        if m in seen:
            print_syntax_err('field modifier "%s" seen twice.' % m, string, loc)
        seen.append(m)
    return toks[0]



## construct a header_declaration object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param string : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_header_declaration(string, loc, toks):
    print "hdr_decl:", toks
    assert len(toks)==1
    hdr = toks[0]
    assert len(hdr)==2  # name and  header_dec_body
    return GP4_Header_Declaration.Header_Declaration( string, loc, hdr_name = hdr[0], hdr_body = hdr[1] )

## construct a field_declaration object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param string : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_field_declaration(string, loc, toks):
    # print "field_decl:", toks
    assert len(toks)==1
    fld = toks[0]
    assert len(fld)>1  # name , bit_width, { optional list_of_modifiers }
    return GP4_Field_Declaration.Field_Declaration( string, loc, fld_name = fld[0], fld_width = fld[1], fld_mods=fld[2:] )



## Construct a new PyParsing Parser for P4
# @return parser object.
def new_GP4_parser() :

    LPAREN, RPAREN, LBRACK, RBRACK, LBRACE, RBRACE = map(Suppress, '()[]{}')
    SEMICOLON, COLON =  map(Suppress, ';:')
    
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



    parser = OneOrMore(header_declaration)
    parser.ignore(cStyleComment)

    # parser.validate( ) # check recursive or not
    # parser.setDebug( )
    #length_exp.validate( )
    #length_exp.setDebug( )

    return parser



####################################################
if __name__ == '__main__' :

    txt = 'length (2+3*fred+2) ;'
    parser = new_GP4_parser()
    print txt
    parsed_data = parser.parseString(txt, True)
    print parsed_data

