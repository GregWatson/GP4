# GP4_Parser_Function_Code.py : Code gen routines for Parser Functions
#
## @package GP4

from GP4_Utilities import field_ref_to_string
import GP4_Exceptions

## Flatten a switch field ref PyParse object
# @param sw_field_ref : PyParsing switch_field_ref object
# @returns flattened list
def flatten_sw_field_ref(sw_field_ref):
    res = []
    if len(sw_field_ref) == 1: # field_ref (not latest or current)
        field_ref =  sw_field_ref[0]
        hdr_ref = field_ref[0]
        res = [hdr_ref[0]]
        if len(hdr_ref)>1: res.append(hdr_ref[1])
        res.append(field_ref[1])
    else: 
        res = sw_field_ref[:]
    # print "flatten_sw_field_ref:", res
    return res


## Generate code to evaluate a single field_ref expression and return value and width tuple.
# @param sw_field_ref : PyParsing switch_field_ref object
# @param p4   : P4 object
# @param result_name : String. Name of local Python variable in which to put the final value.
# @returns [code] 
def gen_eval_switch_field_ref_code( sw_field_ref, p4, result_name, width_name ):
    """ 
    sw_field_ref is field_ref or 'latest.' + field_name   or  'current' + 2 values
    """
    print "gen_eval_field_ref_code: field_ref=",sw_field_ref

    if len(sw_field_ref) == 1: # field_ref (not latest or current)
        field_ref =  sw_field_ref[0]
        if not p4.is_legal_field_ref(field_ref):
            print "Error: Field ref '%s' unknown." % field_ref_to_string(field_ref)
            sys.exit(1)  # fixme

    # need to create argument string to pass to function that will evaluate 
    # switch ref at run time.

    args = flatten_sw_field_ref(sw_field_ref)
    print args
    code = '(%s, %s) = p4.get_sw_field_ref_value_and_width(%s, bits)' % \
                (result_name, width_name, str(args))
    return code





## Generate code to evaluate a return switch expression in the named variable
# @param switch_exp : PyParsing list of switch_field_ref expressions
# @param p4   : P4 object
# @param result_name : String. Name of local Python variable in which to put the final value.
# @returns [code] 
def gen_switch_exp_code(switch_exp, p4, result_name):
    """ switch_exp is a list of field_refs. We need to:
        1. check they are valid (defined)
        2. get their value and width
        3. concatentate them to form a single bit vector.
    """
    print "gen_switch_exp_code", switch_exp

    codeL = []
    assert len(switch_exp)
    for ix,field_ref in enumerate( switch_exp ):

        code = gen_eval_switch_field_ref_code( field_ref, p4, 'sw_val', 'sw_width' )
        codeL.append(code)

        if ix == 0 : # first value
            codeL.append( '%s = sw_val' % result_name )

        else:
            codeL.append('%s = (%s << sw_width) + sw_val' % (result_name, result_name))

    print codeL
    return codeL




## Generate code to evaluate a return switch case entry expression.
# @param c_e : PyParsing case_entry
# @param p4  : P4 object
# @param var_name : String. Name of local Python variable to compare against
# @param is_first : Bool. True if this is first case expression in the switch statement.
# @returns is_default, [code] .  is_default is True if this is a 'default' case.
def gen_switch_case_entry_code(c_e, p4, var_name, is_first):
    """ c_e is like:
              [[['0']],             'GET_TYPE0' ]
              [[['1'], ['3', '7']], 'xxxxxx'    ]
              [['default'],         'NEXT_STATE']
    """
    print "gen_switch_case_entry_code:", c_e
    assert len(c_e) == 2
    caseL      = c_e[0]
    next_state = c_e[1]

    # check target state exists
    if next_state != 'P4_PARSING_DONE':
        if not p4.get_parse_function(next_state):
            raise GP4_Exceptions.RuntimeError, "Unknown parser state: '%s'" % next_state

    if caseL[0] == 'default': 
        if is_first: return (True, ["next_state = '%s'" % next_state])
        else:        return (True, ["else: next_state = '%s'" % next_state])

    # not default, must be list of values or (value,mask) pairs
    codeL = []
    for el in caseL:
        text = 'if' if is_first else 'elif'
        if len(el)==1: # simple value
            codeL.append( text + " %s == %s: next_state = '%s'" % (var_name, el[0], next_state) )
        else: #value mask
            codeL.append( text + " (%s & %s) == %s: next_state = '%s'" % (var_name, el[1], el[0], next_state) )
        is_first = False
    
    return False, codeL
