# GP4_PyParse_Actions.py   - Parsing Action definitions.
#
## @package GP4

import GP4_Header_Declaration
import GP4_Field
import GP4_Header_Instance
import GP4_Header_Stack
import GP4_Parser_Function
import GP4_Control_Function
import GP4_Table

from GP4_Utilities import *
import sys



## compute bit width. '*' becomes zero.
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_bit_width(string, loc, toks):
    # print "do_bit_width:",toks[0]
    if toks[0] == '*': toks[0] = 0
    elif toks[0].startswith('0x'): 
        toks[0] = int(toks[0][2:],16)
    else: toks[0] = int(toks[0]) 





## construct a field modifier list (check valid)
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
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
# @param toks : Tokens.  List of tokens representing this object.
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
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_field_declaration(string, loc, toks):
    # print "field_decl:", toks
    assert len(toks)==1
    fld = toks[0]
    assert len(fld)>1  # name , bit_width, { optional list_of_modifiers }
    return [ GP4_Field.Field( 
                string, loc, 
                fld_name = fld[0], fld_width = fld[1], fld_mods=fld[2:] ) ]


## construct a header instance or header stack object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_instance_declaration(string, loc, toks):
    # print "inst_decl:", toks
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
            max_inst_val = get_integer(inst[2])
    if is_array: 
        return [ GP4_Header_Stack.Header_Stack( 
            string, loc, 
            hdr_type_name    = type_name,
            hdr_is_metadata  = is_metadata,
            hdr_inst_name    = inst_name,
            hdr_max_inst_val = max_inst_val) ]

    else:
        return [ GP4_Header_Instance.Header_Instance( 
            string, loc, 
            hdr_type_name    = type_name,
            hdr_is_metadata  = is_metadata,
            hdr_inst_name    = inst_name ) ]


    
## construct a Parser Function object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_parser_function(string, loc, toks):
    print "parser_function:", toks
    assert len(toks)==1
    fun = toks[0]
    assert len(fun)==2  # name , body
    name      = fun[0]
    func_body = fun[1]
    return [ GP4_Parser_Function.Parser_Function(
                string, loc, name, func_body 
            ) ]





## add "do_ctrl_func" to token list to make it easy to parse the stateemnt later
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token starting with string "do_ctrl_func" 
def do_apply_control_function_statement(string, loc, toks):
    toks[0] = ['do_ctrl_func', toks[0][0] ]


## construct a Control Function object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_control_function(string, loc, toks):
    print "control_function:", toks
    
    my_toks = toks.asList()
    assert len(my_toks)==1
    fun = my_toks[0]
    assert len(fun)==2  # name , body
    name      = fun[0]
    func_body = fun[1]
    return [ GP4_Control_Function.Control_Function(
                string, loc, name, func_body 
            ) ]


## construct a valid_header_ref object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_valid_header_ref(string, loc, toks):
    """ Convert it to code that checks validity of header.
    """
    #print "do_valid_header_ref:", toks
    hdrL = toks[0]
    hdr_name = hdrL[0]
    hdr_index = hdrL[1] if len(hdrL)>1 else '""'
    toks[0] = ['p4.check_hdr_inst_is_valid("%s", hdr_index=%s)' % (hdr_name, hdr_index) ]

## construct a get_field_ref object (make code to get value)
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_get_field_ref(string, loc, toks):
    """ Convert it to code that gets value of field_ref
    """
    print "do_get_field_ref:", toks
    f_refL = toks[0]
    field_name = f_refL[1]
    hdr_refL = f_refL[0]
    hdr_name = hdr_refL[0]
    hdr_index = hdr_refL[1] if len(hdr_refL)>1 else '""'
    toks[0] = ['p4.get_hdr_inst("%s", hdr_index=%s).get_field_value("%s")' 
            % (hdr_name, hdr_index, field_name) ]


    
## construct a Table object
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @param toks : Tokens.  List of tokens representing this object.
# @return new token containing the constructed object.
def do_table_declaration(string, loc, toks):
    print "table_declaration:", toks
    
    my_toks = toks.asList()
    assert len(my_toks)==1
    table   = my_toks[0]
    name    = table[0]
    actions = []
    field_matches = []
    min_size = 0
    max_size = 0

    for el in table[1:] :
        assert len(el)>1,"Expected table element to have a type string and a value. Saw %s" % `el`
        el_type = el[0]
        if el_type == 'min_size': 
            min_size = get_integer(el[1])
        elif el_type == 'max_size': 
            max_size = get_integer(el[1])
        elif el_type == 'reads':
            field_matches = el[1:]
        elif el_type == 'actions':
            actions = el[1:]
        else:
            assert False,"Unknown Table element type: %s" % el_type

    return [ GP4_Table.Table(
                string, loc, name, 
                field_matches=field_matches, 
                actions=actions, 
                min_size=min_size, 
                max_size=max_size
            ) ]


