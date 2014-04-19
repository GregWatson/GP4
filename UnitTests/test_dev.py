##################################################
#
# test_dev.py - development tests
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Work/GP4/src")
try:
    from GP4.GP4_CompilerHelp import compile_string
    from GP4.GP4_Packet_Parser import parse_packet
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

## Compile and run a GP4 program provided as a string.
# @param program : String.  The program.
# @param pkt     : [ byte ] i.e. list of integers
# @param init_state : String. Name of initial parser state
# @param debug   : Integer. Debug flags
# @return (err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.
def parse_and_run_test(program, pkt, init_state='start', debug=0):

    p4 = compile_string( program=program )

    if not p4:
        print "Hmmm. Syntax error?"
  
    err, bytes_used = parse_packet(p4, pkt, init_state)

    return (err, bytes_used)


    
class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass
    

    """ Test header decl and header insts  -----------------------------------------"""
    def test1(self, debug=1):

        program = """

header vlan_tag {
    fields {
        pcp : 3 signed, saturating;
        vid : 12;
        ethertype : 16; 
        vid2 : 9;
    }
    length (2+1) ; 
    max_length 33;
}

header hdr2 {fields { a : 8 ; } }

vlan_tag metadata vlan_instance;
vlan_tag vlan_instance_stack [ 5 ]; 

"""
        p4 = simple_test(program, debug=debug)


    """ Test syntax error handling ---------------------------------------------------"""
    def test2(self, debug=1): 

        program = """ header vlan_tag { }"""
        try:
            p4 = simple_test(program, debug=debug)
        except GP4.GP4_Exceptions.SyntaxError,err:
            print "Syntax Error was expected"


    """ Test parser funcs ------------------------------------------------------------"""
    def test3(self, debug=1):

        program = """
parser we_are_done  { return P4_PARSING_DONE ; }
parser nxt_is_done  { return we_are_done ; }
parser prsr_switch  { return switch ( L2.DA ) { 1 : nxt_state ; } } 
parser prsr_switch2 { return switch ( L2.DA, L2.SA ) { 
                        12 : nxt_is_done; 
                        5, 9 : five_or_nine;
                        800 mask 22,99  : masked_state;
                        default : def_state;
                     } }
parser do_stuff { extract ( L2_hdr ) ;
                  extract ( vlan_id[3] );
                  extract ( ip_hdr[next] ); 
                  set_metadata ( hdr.f1, 666 );
                  return P4_PARSING_DONE ; 
                }

"""
        p4 = simple_test(program, debug=debug)



    """ Test parser runtime ------------------------------------------------------------"""
    def test4(self, debug=1):

        program = """
header L2_def {
    fields { DA : 48; SA : 48; }
}
header L9_def {
    fields { type : 5; three_bits : 3; }
}

L2_def L2_hdr;
L9_def L9_hdr;

parser start  { extract ( L2_hdr ) ; 
                return DO_L9 ;
              }
parser DO_L9  { extract ( L9_hdr ) ; 
                return P4_PARSING_DONE ; 
              }
"""
        pkt = [ i for i in range(20) ]
        (err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)

        self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
        self.assert_( num_bytes_used == 13, 'Expected 13 bytes consumed, Saw %d.' % num_bytes_used )


    """ Test parser runtime ------------------------------------------------------------"""
    def test5(self, debug=1):

        program = """
header L2_def {
    fields { DA : 48; SA : 48; }
}

L2_def L2_hdr[2];

parser start  { extract ( L2_hdr[0] ) ; 
                return DO_L2 ;
              }
parser DO_L2  { extract ( L2_hdr[next] ) ; 
                return P4_PARSING_DONE ; 
              }
"""
        pkt = [ i for i in range(20) ]
        try:
            (err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.RuntimeError,err:
            print "RUntime Error was expected"



    """ Test parser. stack err ------------------------------------------------------------"""
    def test5a(self, debug=1):

        program = """
header L2_def {
    fields { DA : 48; SA : 48; }
}

L2_def L2_hdr[2];

parser start  { extract ( L2_hdr[2] ) ;  /* out of range */
                return P4_PARSING_DONE ;
              }

"""
        pkt = [ i for i in range(20) ]
        try:
            (err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Runtime Error was expected."
            print err[0][0]

    """ Test parser. run time stack err ------------------------------------------------------------"""
    def test5b(self, debug=1):

        program = """
header L2_def {
    fields { DA : 48; SA : 48; }
}

L2_def L2_hdr[1];

parser start  { extract ( L2_hdr[0] ) ;
                return P4_ERR ;
              }
parser P4_ERR { extract ( L2_hdr[next] ) ;  /* out of range */
                return P4_PARSING_DONE ;
              }

"""
        pkt = [ i for i in range(20) ]
        try:
            (err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Runtime Error was expected."




    """ Test parser runtime ------------------------------------------------------------"""
    def test6(self, debug=1):

        program = """
header L2_def {
    fields { DA : 48; SA : 48; }
}

L2_def L2_hdr[5];

parser start  { extract ( L2_hdr[0] ) ; 
                return GET_L2_1 ;
              }
parser GET_L2_1  { extract ( L2_hdr[next] ) ; 
                   return GET_L2_2 ; 
                 }
parser GET_L2_2  { extract ( L2_hdr[2] ) ; 
                   return GET_L2_3 ; 
                 }
parser GET_L2_3  { extract ( L2_hdr[next] ) ; 
                   return GET_L2_4 ; 
                 }
parser GET_L2_4  { extract ( L2_hdr[4] ) ; 
                   return  P4_PARSING_DONE ; 
                 }
"""
        
        exp_bytes_used = 5*12
        pkt = [ i for i in range(60) ]

        try:

            (err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))

        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Unexpected Runtime Error:",err
            self.assert_(False)


    """ Test parser set metadata ------------------------------------------------------------"""
    def test7(self, debug=1):

        program = """
header L2_def {
    fields { DA : 48; SA : 48; }
}
header meta_def {
    fields { number: 32 ; }
}

L2_def    L2_hdr;
meta_def  metadata  meta;

parser start  { extract ( L2_hdr ) ; 
                return GET_META ;
              }
parser GET_META  { set_metadata ( meta.nunber, 1234 ) ; 
                   return  P4_PARSING_DONE ; 
                 }
"""
        
        exp_bytes_used = 1*12
        pkt = [ i for i in range(12) ]

        try:

            (err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))

        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Unexpected Runtime Error:",err
            self.assert_(False)







if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    single = unittest.TestSuite()
    single.addTest( test_dev('test7' ))
    unittest.TextTestRunner().run(single)
