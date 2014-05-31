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


    """ Test table min max  -----------------------------------------"""
    def test200(self, debug=1):

        program = """
header L3_def { fields { stuff : 32; }  }

L3_def L3_hdr[3];

parser start  { extract ( L3_hdr[next] ); 
                return P4_PARSING_DONE ; }

control ingress { 
    apply_table( my_table );
}

table my_table { 
    actions { some_action ; }
    min_size 23;
    max_size 1024;
}

"""

        exp_bytes_used = 4
        pkt = [ i for i in range(exp_bytes_used)]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        init_ctrl='ingress', debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L3_hdr[0].stuff', 0x10203)
            self.check_table( p4, 'my_table', min_size=23, max_size =1024)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)


    """ Test table min max  -----------------------------------------"""
    def test201(self, debug=1):

        program = """
header L3_def { fields { stuff : 32; }  }

L3_def L3_hdr[3];

parser start  { extract ( L3_hdr[next] ); 
                return P4_PARSING_DONE ; }

control ingress { 
    apply_table( my_table );
}

table my_table { 
    reads { L3_hdr[0].stuff : exact ; 
            L3_hdr[0].stuff mask 0xff : ternary ; 
    }
    actions { some_action ; }
    min_size 1;
}

"""

        exp_bytes_used = 4
        pkt = [ i for i in range(exp_bytes_used)]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        init_ctrl='ingress', debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L3_hdr[0].stuff', 0x10203)
            self.check_table( p4, 'my_table', min_size=1)

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
        single.addTest( test_dev('test201' ))
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
