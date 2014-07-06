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

    """ Test deparser for long words and weird bit offsets -----------------------------"""
    def test301(self, debug=1):

        program = """
layout vlan_tagish {
    fields {
        pcp : 3 ;
        vid : 12;
        da  : 48 ;
        sa  : 48 ;
        t18 : 18; 
        vid2 : 15;
    }
}

vlan_tagish V1;

parser start  { extract ( V1 ) ; return P4_PARSING_DONE ; }

control ingress { 
    apply_table( table1 );
}

table table1 { 
    actions { do_my_action ; } 
}

action do_my_action() { 

    add_to_field(V1.pcp, 0x4) ;
    add_to_field(V1.vid, 0xf00) ;
    add_to_field(V1.t18, 0x10000) ;
    add_to_field(V1.vid2, 0x2000) ;
    modify_field(V1.da, V1.sa);
    modify_field(V1.sa, V1.da);
}

"""

        try:
            p4, runtime = create_P4_and_runtime(program)

            setup_cmds  = ['table1.set_default_action( do_my_action() )'] 
            run_cmds( p4, runtime, setup_cmds )

            #                
            pkts = [ [ i for i in range(20) ] ]
            exp_pkts_out = [ [0x9e, 1,8,9,0xa, 0xb, 0xc, 0xd, 2,3,4,5,6,7, 0x8e, 0xf, 0x30, 17,18,19 ] ]
            exp_bytes_used = 18

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
            self.check_field( p4, 'V1.pcp', 0x4) 
            self.check_field( p4, 'V1.vid', 0xf00) 
            self.check_field( p4, 'V1.da', 0x840485058606) 
            self.check_field( p4, 'V1.sa', 0x810182028303) 
            self.check_field( p4, 'V1.vid2', 0x3011) 
            self.check_field( p4, 'V1.t18', 0x31c1e) 
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
        single.addTest( test_dev('test301' ))
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
