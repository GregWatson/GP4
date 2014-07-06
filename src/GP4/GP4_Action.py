# GP4_Action.py : P4 Action Object
#
## @package GP4

from GP4_Utilities  import *
#from GP4_Parser_Function_Code import *
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

class Action(AST_object):

    ## Construct new Action object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the Action
    # @param func   : Function. Performs the action
    # @param func_args : [ String ] : formal params from Pyparsing
    # @param func_body : [ Pyparsing objects ] : action statements from Pyparsing
    # @param num_args  : Integer. Number of args if primitive (auto deduced for user defined actions)
    # @returns self
    def __init__(self, string, loc, name, func=None, func_args=[], func_body = [], num_args=0 ):
        
        super(Action, self).__init__(string, loc, 'action')

        self.name      = name
        self.func_args = func_args
        self.func_body = func_body
        self.num_args  = num_args 
        if len(func_args): self.num_args =  len(func_args)
        self.func      = func   # Function associated with this action. May take params.

   
    ## Compile action if not already compiled.
    # @param self : object
    # @param p4   : p4 object
    # @returns None
    def check_self_consistent(self, p4):
        print "Action", self.name,"check self consistent."
        if self.func_body:
            self.func = self.compile(p4) 


    ## Execute the action in the context of P4, given zero or more arguments
    # @param self : object
    # @param p4   : p4 object
    # @param args : some args
    # @returns None
    def execute(self, p4, *args):
        print "Executing action",self.name,"args:",args
        if not self.func:
            raise GP4_Exceptions.RuntimeError, "Action '%s'\'s function is not yet defined." % self.name
        self.func(p4, *args)


    ## Compile a user-defined action. 
    # @param self : object
    # @returns None.   Sets self.func
    def compile(self, p4):
        """ Body defined in self.func_body and args in self.func_args.
            Compile a Python function that will execute this and store it in self.func.
            self.func has signature:   f(p4, *args) and returns nothing.

            Replace formal params with arg[i]
            So the user defined action:

                do_action( arg1, arg2 ) {
                    modify_field( arg1, 0x33, arg2 )
                }

            becomes the Python code:

                def f(p4, *args):
                    p4.execute_action_by_name('modify_field', args[0], 0x33, args[1])
        """
        body = self.func_body
        args = self.func_args
        print "    act compile:\n   body=", body,"\n   args=", args
        
        codeL = [ 'def f(p4, *args):' ]
        codeL.append('   if len(args) != %d:' % len(args))
        codeL.append('      raise GP4_Exceptions.RuntimeError, \\')
        codeL.append('          "Action ' + self.name + ' expected %d' % len(args) + r' args but was passed %d args." % len(args)')

        for fn in body:
            fn_name = fn[0]
            print "compiling:",fn
            action = p4.get_action_by_name(fn_name)
            if not action:
                raise GP4_Exceptions.RuntimeError, 'In action "%s" call to action "%s" undefined' % \
                    (self.name, fn_name)

            num_fn_args = len(fn)-1
            if num_fn_args < action.num_args:
                raise GP4_Exceptions.RuntimeError, 'In action "%s" call to action "%s" has %d args but expected at least %d.' % \
                    (self.name, fn_name, num_fn_args, action.num_args)
            

            if len(fn)==1:  # no args
                code = "   p4.execute_action_by_name('%s')" % fn[0]

            else: # args
                code = "   p4.execute_action_by_name('%s'" % fn[0]

                for ix,arg in enumerate(fn[1:]):
                    if len(arg) == 1:  # only check to see if its a formal arg if it has length 1
                        formal = arg[0]
                        if formal in args:
                            code += ", args[%d]" % args.index(formal)
                            continue
                    code += ", %s" % str(arg)

                code += ')'

            codeL.append(code)
            
        # compile the code into a local function
        fn = compile_list_of_python(codeL)
        return fn



#######################
# Built-in Actions
#######################


## Built-in Action no_action
# @returns None
def no_action(p4):
    print "   no_action: Doing nothing..."



## Built-in Action add_to_field
# @param field : field to be added-to
# @param value : field or constant to add
# @returns None
def add_to_field(p4, field_ref, fld_or_val):
    print "   Action add_to_field(field=",field_ref,", value=",fld_or_val,")"
    fld = p4.get_field_from_field_ref(field_ref)
    if not fld:
        raise GP4_Exceptions.RuntimeError, "Unknown field : %s" % str(field_ref)
    
    value = get_value_of_fld_or_val(p4, fld_or_val)
    new_value = fld.get_value() + value
    print "Set",field_ref,"to 0x%x" % new_value
    fld.set_value(new_value)



## Built-in Action modify_field
# @param field : field to be added-to
# @param value : field or constant to add
# @param mask  : integer (optional)
# @returns None
def modify_field(p4, field_ref, fld_or_val, mask=None):
    print "   Action modify_field(field=",field_ref,", value=",fld_or_val,
    if mask != None: print ", mask=0x%x" % mask,")"
    else: print ")"

    hdr_i = p4.get_header_from_field_ref(field_ref)
    if not hdr_i: return
    if not hdr_i.fields_created : return  # hdr invalid

    fld = p4.get_field_from_field_ref(field_ref)
    if not fld:
        raise GP4_Exceptions.RuntimeError, "Unknown field : %s" % str(field_ref)
    
    value = get_value_of_fld_or_val(p4, fld_or_val)
    if mask != None:
        value &= mask
        value = (fld.get_value() & ~mask) | value

    print "Set",field_ref,"to 0x%x" % value
    fld.set_value(value)



#######################
# Utilities
#######################

## Get the value of argument which is either a value (constant) or a field ref
# @param p4 : p4 object
# @param fld_or_val : field to get value of.
# @returns integer
def get_value_of_fld_or_val(p4, fld_or_val):
    print "get_value_of_fld_or_val", fld_or_val

    if type(fld_or_val) is list:  # field_ref
        return p4.get_field_from_field_ref(fld_or_val).get_value()
    else:
        return get_integer(fld_or_val)
