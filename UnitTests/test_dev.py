##################################################
#
# test_dev.py - development tests
#
##################################################

import sys, unittest, re
sys.path.append("/home/gwatson/Work/GP4/src")
try:
    from GP4.GP4_CompilerHelp import compile_string
    from GP4.GP4_Packet_Parser import parse_packet
    import GP4.GP4_Exceptions
except ImportError, err:
    print "Unable to load GP4 libs. sys.path is:"
    for p in sys.path: print "\t",p
    print err

from GP4_Test import simple_test, parse_and_run_test, GP4_Test

    
class test_dev(GP4_Test):

    """ Test duplicate ctrl func name  -----------------------------------------"""
    def test101(self, debug=1):

        program = """
control my_ctrl_fun { apply_table( fred);  }
control my_ctrl_fun { apply_table( fred);  }
"""

        exp_bytes_used = 5
        pkt = [ 5+i for i in range(8) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( False, 'Expected to see Syntax Error about Control func name already defined.' )
        except GP4.GP4_Exceptions.SyntaxError as err:
            print "Expected Syntax Error",err.data
            self.assert_(True)



    """ Test ctrl func  -----------------------------------------"""
    def test102(self, debug=1):

        program = """
header L2_def { fields { DA : 48; SA : 48; EthType : 16; }  }

L2_def L2_hdr;

parser start  { extract ( L2_hdr ) ; return P4_PARSING_DONE ; }

control ingress { 
    /* if ( valid ( L2_hdr) and ( L2_hdr.DA == 1234 ) ) { apply_table(a_table); } */
    if ( L2_hdr.DA == 4328719365 ) { apply_table(a_table); } /* 0x102030405 */
    else {
        do_another_ctrl_func ( ) ;
    }
    do_another_ctrl_func() ;
}

control do_another_ctrl_func {  apply_table(a_table); }

table a_table { }

"""

        exp_bytes_used = 14
        pkt = [ i for i in range(14) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        init_ctrl='ingress', debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            #self.check_field( p4, 'L2_hdr.type0', 0x5 )
            #self.check_field( p4, 'Type_1_hdr.four', 0x6070809 )

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)



if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    if (True):
        single = unittest.TestSuite()
        single.addTest( test_dev('test102' ))
        unittest.TextTestRunner().run(single)

    else:
        program = """
header L2_def {    fields { DA : 48; SA : 48; }   }
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
