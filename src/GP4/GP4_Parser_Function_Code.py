# GP4_Parser_Function_Code.py : Code gen routines for Parser Functions
#
## @package GP4

from GP4_Utilities import field_ref_to_string

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
    code = '(%s, %s) = p4.get_sw_field_ref_value_and_width(%s, p4, bits)' % \
                (result_name, width_name, str(args))
    print code
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

    assert len(switch_exp)
    codeL = []
    for ix,field_ref in enumerate( switch_exp ):

        eval_code = gen_eval_switch_field_ref_code( field_ref, p4, result_name, 'width' )



    return []
