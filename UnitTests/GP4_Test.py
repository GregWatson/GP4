##################################################
#
# GP4_Test.py - Base class for development tests
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Work/GP4/src")
try:
    from GP4.GP4_CompilerHelp  import compile_string
    from GP4.GP4_Runtime       import Runtime
    from GP4.GP4_Execute       import run_control_function
    from GP4.GP4_Utilities     import *

    import GP4.GP4_Exceptions
except ImportError, err:
    print "Unable to load GP4 libs. sys.path is:"
    for p in sys.path: print "\t",p
    print err

## Compile and run a GP4 program provided as a string.
# @param program : String.  The program.
# @param debug   : Integer. Debug flags
# @return the P4 object
def simple_test(program, debug=0):
    ''' Given a string (GP4 program) in program, compile and run it.
    '''
    p4 = compile_string( program=program )

    if not p4:
        print "Hmmm. Syntax error?"
    else:
        print p4

    return p4


## Create P4 object from program and a runtime to go with it.
# @param program : String.  The program.
# @param debug   : Integer. Debug flags
# @return ( P4 object, runtime object )
def create_P4_and_runtime(program, debug=0):
    ''' Given a string (GP4 program) in program, compile it and create P4
    '''
    p4 = simple_test(program, debug)

    runtime = Runtime(p4)

    p4.check_self_consistent()

    return (p4 , runtime)



## Compile and run a GP4 program provided as a string.
# @param program : String.  The program.
# @param pkt     : [ byte ] i.e. list of integers
# @param init_state : String. Name of initial parser state
# @param init_ctrl  : String. Name of initial control function. If None then dont execute
# @param debug   : Integer. Debug flags
# @return (p4, err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.
def parse_and_run_test(program, pkt, init_state='start', init_ctrl='', debug=0):

    p4 = compile_string( program=program )

    if not p4:
        print "Hmmm. Syntax error?"
        sys.exit(1)

    runtime = Runtime(p4)

    p4.check_self_consistent()

    err, bytes_used = runtime.parse_packet(pkt, init_state)

    if err:
        return (p4, err, bytes_used)

    if init_ctrl: run_control_function(p4, pkt, init_ctrl )

    return (p4, '', bytes_used )



## Compile and run a sequence of GP4 Runtime commands provided as strings.
# @param program    : String.  The program.
# @param setup_cmds : [ runtime_cmds ].  Things to do before parsing the first packet.
# @param pkts       : [ [ byte ] ] i.e. list of list of integers
# @param init_state : String. Name of initial parser state
# @param init_ctrl  : String. Name of initial control function. If None then dont execute
# @param debug      : Integer. Debug flags
# @return (p4, err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.
def setup_tables_parse_and_run_test( program, setup_cmds=[], pkts=[], 
                                     init_state='start', init_ctrl='', debug=0):

    p4, runtime = create_P4_and_runtime(program, debug=0)

    for cmd in setup_cmds: 
        runtime.run_cmd(cmd)

    total_bytes_used = 0

    for pkt in pkts:

        err, bytes_used = runtime.parse_packet(pkt, init_state)

        if err:
            return (p4, err, bytes_used)

        if init_ctrl: run_control_function(p4, pkt, init_ctrl )

        total_bytes_used += bytes_used

    return (p4, '', total_bytes_used )




## Compile and run a sequence of GP4 Runtime commands provided as strings.
# @param p4         : p4 object
# @param runtime    : runtime object
# @param setup_cmds : [ runtime_cmds ]. 
# @return None
def run_cmds( p4, runtime, setup_cmds=[] ):

    for cmd in setup_cmds: 
        runtime.run_cmd(cmd)




## Given P4 and runtime, process a bunch of packets.
# @param p4         : p4 object
# @param runtime    : runtime object
# @param pkts       : [ [ byte ] ] i.e. list of list of integers
# @param init_state : String. Name of initial parser state
# @param init_ctrl  : String. Name of initial control function. If None then dont execute
# @param debug      : Integer. Debug flags
# @return ( err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.
def process_pkts(p4, runtime, pkts=[], init_state='start', init_ctrl='', debug=0):

    total_bytes_used = 0

    for pkt in pkts:

        err, bytes_used = runtime.parse_packet(pkt, init_state)

        if err:
            return (err, bytes_used)

        if init_ctrl: run_control_function( p4, pkt, init_ctrl )

        total_bytes_used += bytes_used

    return ('', total_bytes_used )




    
class GP4_Test(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass

    ## Check that the specified field has the specified value
    # @param self : test
    # @param p4   : p4 object
    # @param field_ref : String.  e.g. 'L2_hdr.DA' or 'vlan[3].my_field'
    # @param val : Integer: expected value or "invalid"
    # @returns None: will assert a failure
    def check_field(self, p4, field_ref, val):
        # extract index, if any
        hdr_name, hdr_index ,field_name = get_hdr_hdr_index_field_name_from_string(field_ref)

        if val == 'invalid':
            self.assert_(not p4.check_hdr_inst_is_valid(hdr_name, hdr_index),
                         "Expected hdr '%s' to be invalid, but was valid." % hdr_name)
            return
            

        # Now get the actual header object from P4.
        hdr_i = p4.get_or_create_hdr_inst(hdr_name, hdr_index)
        self.assert_( hdr_i,"Unable to find header from field ref:" + field_ref)

        act_val = hdr_i.get_field_value(field_name)
        if act_val == None and val == None: return

        self.assert_( act_val != None, 
                "Field %s returned value None: incorrect field name perhaps?" % field_ref )

        self.assert_( act_val == val, "Expected field %s to have value 0x%x but saw 0x%x" % 
                        ( field_ref, val, act_val ) )


    ## Check that the specified table has the specified props
    # @param self : test
    # @param p4   : p4 object
    # @param table_name : String.  
    # @param min_size : Integer: expected min_size
    # @param max_size : Integer: expected max_size
    # @returns None: will assert a failure
    def check_table(self, p4, table_name, min_size=None, max_size=None):
        tbl = p4.get_table(table_name)
        self.assert_( tbl,"Table '%s' is not defined." % table_name)
         
        if min_size != None:
            self.assert_( tbl.min_size == min_size, 
            "Table '%s' min_size is %s but expected %s." % (table_name, `tbl.min_size`, `min_size`))
        if max_size != None:
            self.assert_( tbl.max_size == max_size, 
            "Table '%s' max_size is %s but expected %s." % (table_name, `tbl.max_size`, `max_size`))
                    
