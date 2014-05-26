# GP4_Execute.py - Execute a control function (runtime)
#
# This will execute a control function in the context of a P4 onject and a header.
#
## @package GP4

from GP4_Utilities import print_syntax_err
import GP4_Exceptions


## Given a P4 object and a packet and a starting function n ame, execute the function.
# @param p4  : P4 object
# @param pkt : [ bytes ]
# @param init_ctrl : name of a control function in P4 object.
# @return None.

def run_control_function(p4, pkt, init_ctrl):

    fun_name = init_ctrl
    
    ctrl_fun = p4.get_control_function(fun_name)

    if not ctrl_fun:
        raise  GP4_Exceptions.RuntimeError , 'Control function "%s" not found' % fun_name

    ctrl_fun.execute( p4 )

    print "Control function", init_ctrl,"completed."
