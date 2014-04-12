# GP4_PyParse_Actions.py   - Parsing Action definitions.
#
## @package GP4

import GP4_Header_Declaration
import GP4_Field_Declaration
import GP4_Header_Instance
from GP4_Utilities import *
import sys



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
    # print "hdr_decl:", toks
    assert len(toks)==1
    hdr = toks[0]
    assert len(hdr)==2  # name and  header_dec_body
    return [ GP4_Header_Declaration.Header_Declaration( string, loc, hdr_name = hdr[0], hdr_body = hdr[1] ) ]

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
    return [ GP4_Field_Declaration.Field_Declaration( 
                string, loc, 
                fld_name = fld[0], fld_width = fld[1], fld_mods=fld[2:] ) ]


## construct a instance_declaration object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param string : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_instance_declaration(string, loc, toks):
    print "inst_decl:", toks
    assert len(toks)==1,"do_instance_declaration: expected one token"
    inst = toks[0]
    assert len(inst)>1 and len(inst)<4,"do_instance_declaration: unexepcted tokens: %s" % str(toks)
    
    type_name = inst[0]
    is_metadata = False
    is_array = False
    max_inst_val = 1
    if inst[1] == 'metadata': 
        is_metadata = True
        inst_name = inst[2]
    else:
        inst_name = inst[1]
        if len(inst)==3:  # must be array
            is_array = True
            max_inst_val = int(inst[2])

    return [ GP4_Header_Instance.Header_Instance( 
            string, loc, 
            hdr_type_name    = type_name,
            hdr_is_metadata  = is_metadata,
            hdr_inst_name    = inst_name,
            hdr_is_array     = is_array,
            hdr_max_inst_val = max_inst_val) ]

    
