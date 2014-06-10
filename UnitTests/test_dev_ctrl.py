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



    """ Test ctrl func ibasic if then else  -----------------------------------------"""
    def test102(self, debug=1):

        program = """
header L2_def { fields { DA : 48; SA : 48; EthType : 16; }  }
header L3_def { fields { stuff : 32; }  }

L2_def L2_hdr;
L3_def L3_hdr[3];

parser start  { extract ( L2_hdr ) ; 
                extract ( L3_hdr[next] );
                extract ( L3_hdr[next] );
                return P4_PARSING_DONE ; }

control ingress { 
    /* if ( valid ( L2_hdr) and ( L2_hdr.DA == 1234 ) ) { apply_table(a_table); } */
    if ( L2_hdr.DA ==  0x102030405 ) { apply_table(a_table); } 
    else {
        do_another_ctrl_func ( ) ;
    }
    if ( L2_hdr.DA ==  0xff ) { apply_table(a_table); } 
    else {
        if ( valid ( L3_hdr[2] ) ) {apply_table(BAD_table); }
        else {
            if ( L3_hdr[1].stuff == 0x12131415 ) {
                do_another_ctrl_func ( ) ;
            }
        }
    }
}

control do_another_ctrl_func {  apply_table(b_table); }

table a_table {    actions { some_action ; } }
table b_table {    actions { some_action ; } }
table BAD_table {    actions { some_action ; } }

action some_action;

"""

        exp_bytes_used = 22
        pkt = [ i for i in range(22)]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        init_ctrl='ingress', debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.DA', 0x102030405 )
            self.check_field( p4, 'L2_hdr.SA', 0x60708090a0b )
            self.check_field( p4, 'L2_hdr.EthType', 0xc0d )
            self.check_field( p4, 'L3_hdr[0].stuff', 0xe0f1011)
            self.check_field( p4, 'L3_hdr[1].stuff', 0x12131415)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)


    """ Test ctrl func bool expr  -----------------------------------------"""
    def test103(self, debug=1):

        program = """
header L2_def { fields { DA : 48; SA : 48; EthType : 16; }  }
header L3_def { fields { byte1 : 8; byte2 : 8; }  }

L2_def L2_hdr;
L3_def L3_hdr[3];

parser start  { extract ( L2_hdr ) ; 
                extract ( L3_hdr[next] );
                extract ( L3_hdr[next] );
                return P4_PARSING_DONE ; }

control ingress { 
    if ( L3_hdr[0].byte1 < L3_hdr[0].byte2 ) 
    { 
        if ( L3_hdr[1].byte1 > L3_hdr[0].byte2 )
        {        
            if ( ( L3_hdr[1].byte1 & L3_hdr[0].byte2) == 0 )
            {
                if ( ( L3_hdr[1].byte2 ^ L3_hdr[0].byte2) == 0x1e )
                {
                    if ( ( L3_hdr[1].byte2 == 0x11 ) and not ( L3_hdr[0].byte2 == 0) )
                    {
                        apply_table (GOOD_table); 
                    }
                }
            }
        }
    }
    else { apply_table (BAD_table); }
}

table GOOD_table {  actions { some_action ; } }
table BAD_table {    actions { some_action ; } }

action some_action;

"""

        exp_bytes_used = 18
        pkt = [ i for i in range(exp_bytes_used)]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        init_ctrl='ingress', debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.DA', 0x102030405 )
            self.check_field( p4, 'L2_hdr.SA', 0x60708090a0b )
            self.check_field( p4, 'L2_hdr.EthType', 0xc0d )
            self.check_field( p4, 'L3_hdr[0].byte1', 0xe)
            self.check_field( p4, 'L3_hdr[0].byte2', 0xf)
            self.check_field( p4, 'L3_hdr[1].byte1', 0x10)
            self.check_field( p4, 'L3_hdr[1].byte2', 0x11)

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
        single.addTest( test_dev('test103' ))
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
