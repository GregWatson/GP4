##################################################
#
# test_dev.py - development tests
#
##################################################

import sys, unittest, re
sys.path.append("/home/gwatson/Work/GP4/src")
try:
    from GP4.GP4_CompilerHelp import compile_string
    import GP4.GP4_Exceptions
except ImportError, err:
    print "Unable to load GP4 libs. sys.path is:"
    for p in sys.path: print "\t",p
    print err

from GP4_Test import simple_test, parse_and_run_test, setup_tables_parse_and_run_test, GP4_Test, \
     create_P4_and_runtime, run_cmds, process_pkts



    
class test_dev(GP4_Test):

    """ Test add header action -----------------------------"""
    def test301(self, debug=1):

        program = """
layout h1 { fields { b8 : 8   ; } }
layout h2 { fields { b16 : 16 ; } }
layout h3 { fields { b24 : 24 ; } }

h1 H1; h2 H2; h3 H3;

parser start  { extract ( H1 ) ; extract ( H3) ; return P4_PARSING_DONE ; }

control ingress { 
    apply_table( table1 );
}

table table1 { 
    actions { do_my_action ; } 
}

action do_my_action() { 
    add_header( H2 );
    modify_field( H2.b16, 0x1234);
}

deparse add_h2_in_middle { H1; H2; H3; }

"""

        try:
            p4, runtime = create_P4_and_runtime(program)

            setup_cmds  = ['table1.set_default_action( do_my_action() )'] 
            run_cmds( p4, runtime, setup_cmds )

            #                
            pkts = [ [ i for i in range(10) ], [5,6,7,8,9 ] ]
            exp_pkts_out = [ [0, 0x12, 0x34, 1,2,3,4,5,6,7,8,9 ], [5,0x12, 0x34,6,7,8,9] ]
            exp_bytes_used = 8

            (err, num_bytes_used, pkts_out ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                       # List of packets
                    init_state = 'start',       # parser start state
                    init_ctrl  = 'ingress',     # control program start
                    debug=debug )

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'H1.b8', 5) 
            self.check_field( p4, 'H2.b16', 0x1234) 
            self.check_field( p4, 'H3.b24', 0x60708) 
            self.check_pkts_out(exp_pkts_out, pkts_out)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data
            self.assert_(False)




    """ Test copy header action -----------------------------"""
    def test302(self, debug=1):

        program = """
layout h1 { fields { b8 : 8   ; } }

h1 H1; h1 H2; h1 H3;

parser start  { extract ( H1 ) ; extract ( H2 ); return P4_PARSING_DONE ; }

control ingress { 
    apply_table( table1 );
}

table table1 { 
    actions { do_my_action ; } 
}

action do_my_action() { 
    add_header( H3 );
    modify_field( H1.b8, 0xff);
    copy_header( H2, H1);
    copy_header( H3, H2);
}

deparse add_h2_in_middle { H1; H2; H3; }

"""

        try:
            p4, runtime = create_P4_and_runtime(program)

            setup_cmds  = ['table1.set_default_action( do_my_action() )'] 
            run_cmds( p4, runtime, setup_cmds )

            #                
            pkts = [ [ i+5 for i in range(6) ] ]
            exp_pkts_out = [ [0xff, 5, 6, 7,8,9,10 ] ]
            exp_bytes_used = 2

            (err, num_bytes_used, pkts_out ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                       # List of packets
                    init_state = 'start',       # parser start state
                    init_ctrl  = 'ingress',     # control program start
                    debug=debug )

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'H1.b8', 0xff) 
            self.check_field( p4, 'H2.b8', 0x5) 
            self.check_field( p4, 'H3.b8', 0x6) 
            self.check_pkts_out(exp_pkts_out, pkts_out)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data
            self.assert_(False)


    """ Test copy invalid header action -----------------------------"""
    def test303(self, debug=1):

        program = """
layout h1 { fields { b8 : 8   ; } }

h1 H1; h1 H2; h1 H3;

parser start  { extract ( H1 ) ; extract ( H2 ); return P4_PARSING_DONE ; }

control ingress { 
    apply_table( table1 );
}

table table1 { 
    actions { do_my_action ; } 
}

action do_my_action() { 
    copy_header( H2, H3);  /* invalidates it */
    copy_header( H1, H3);  /* invalidates it */
}

deparse add_h2_in_middle { H1; H2; H3; } /* None are valid */

"""

        try:
            p4, runtime = create_P4_and_runtime(program)

            setup_cmds  = ['table1.set_default_action( do_my_action() )'] 
            run_cmds( p4, runtime, setup_cmds )

            #                
            pkts = [ [ i+5 for i in range(6) ] ]
            exp_pkts_out = [ [ 7,8,9,10 ] ]
            exp_bytes_used = 2

            (err, num_bytes_used, pkts_out ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                       # List of packets
                    init_state = 'start',       # parser start state
                    init_ctrl  = 'ingress',     # control program start
                    debug=debug )

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_header( p4, 'H1', 'invalid') 
            self.check_header( p4, 'H2', 'invalid') 
            self.check_header( p4, 'H3', 'invalid') 
            self.check_pkts_out(exp_pkts_out, pkts_out)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data
            self.assert_(False)




########################################################################################
if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    if (True):
        single = unittest.TestSuite()
        single.addTest( test_dev('test303' ))
        unittest.TextTestRunner().run(single)

    else:
        program = """
layout L2_def {    fields { DA : 48; SA : 48; }   }
L2_def L2_hdr[1];
parser start  { extract ( L2_hdr[0] ) ;
                return P4_ERR ;
              }
"""
        pkt = [ i for i in range(20) ]
        try:
            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=0)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "test5c: SyntaxError was expected:", ex_err.args
            print "len args is",len(ex_err.args)
