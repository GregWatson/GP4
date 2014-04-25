# GP4_Parser_Function_Code.py : Code gen routines for Parser Functions
#
## @package GP4


## Generate code to evaluate a field_ref expression and return value in the named variable
# @param field_ref : PyParsing field_ref object
# @param p4   : P4 object
# @param result_name : String. Name of local Python variable in which to put the final value.
# @returns [code] 
def gen_eval_field_ref_code( field_ref, p4, result_name ):

    Greg
        Need to check field ref is legal (was defined)
        Need to check field ref is valid (was extracted)
        Then return value

    pass




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
    for ix,field_ref in enumerate switch_exp:

        eval_code = gen_eval_field_ref_code( field_ref, p4, result_name )



    return []
