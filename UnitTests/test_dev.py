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
# @return (p4, err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.
def parse_and_run_test(program, pkt, init_state='start', debug=0):

    p4 = compile_string( program=program )

    if not p4:
        print "Hmmm. Syntax error?"
        sys.exit(1)
  
    err, bytes_used = parse_packet(p4, pkt, init_state)

    return (p4, err, bytes_used)


    
class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass

    ## Check that the specified field has the specified value
    # @param self : test
    # @param p4   : p4 object
    # @param field_ref : String.  e.g. 'L2_hdr.DA' or 'vlan[3].my_field'
    # @param val : Integer: expected value
    # @returns None: will assert a failure
    def check_field(self, p4, field_ref, val):
        # extract index, if any
        tmatch = re.match( r'([a-zA-Z0-9_]+)\[([a-zA-Z0-9_]+)\]\.([a-zA-Z0-9_]+)', field_ref)
        if tmatch:
            hdr_name   = tmatch.group(1)
            hdr_index  = int(tmatch.group(2))
            field_name = tmatch.group(3)
        else:
            tmatch = re.match( r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', field_ref)
            if tmatch:
                hdr_name   = tmatch.group(1)
                hdr_index  = ''
                field_name = tmatch.group(2)
            else:
                print "check_field: unable to parse field_ref:", field_ref
                sys.exit(1)
        # Now get the actual header object from P4.
        hdr_i = p4.get_or_create_hdr_inst(hdr_name, hdr_index)
        self.assert_( hdr_i,"Unable to find header from field ref:" + field_ref)

        act_val = hdr_i.get_field(field_name)
        if act_val == None and val == None: return

        self.assert_( act_val != None, 
                "Field %s returned value None: incorrect field name perhaps?" % field_ref )

        self.assert_( act_val == val, "Expected field %s to have value 0x%x but saw 0x%x" % 
                        ( field_ref, val, act_val ) )
                    

    

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
        (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)

        self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
        self.assert_( num_bytes_used == 13, 'Expected 13 bytes consumed, Saw %d.' % num_bytes_used )
        self.check_field( p4, 'L2_hdr.DA', 0x102030405 )
        self.check_field( p4, 'L2_hdr.SA', 0x60708090a0b )
        self.check_field( p4, 'L9_hdr.type', 1 )
        self.check_field( p4, 'L9_hdr.three_bits', 4 )


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
            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Runtime Error was expected"



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
            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Runtime Error was expected."
            print err



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
            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.RuntimeError, ex_err:
            print "Runtime Error was expected:", ex_err




    """ Test parser. bad return state err ------------------------------------------------------------"""
    def test5c(self, debug=1):

        program = """
header L2_def {    fields { DA : 48; SA : 48; }   }
L2_def L2_hdr[1];
parser start  { extract ( L2_hdr[0] ) ;
                return P4_ERR ;
              }
"""
        pkt = [ i for i in range(20) ]
        try:
            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', debug=debug)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "test5c: SyntaxError was expected:", ex_err




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

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))

            self.check_field( p4, 'L2_hdr[0].DA', 0x102030405 )
            self.check_field( p4, 'L2_hdr[0].SA', 0x60708090a0b )
            self.check_field( p4, 'L2_hdr[1].DA', 0x0c0d0e0f1011 )
            self.check_field( p4, 'L2_hdr[1].SA', 0x121314151617 )
            self.check_field( p4, 'L2_hdr[2].DA', 0x18191a1b1c1d )
            self.check_field( p4, 'L2_hdr[2].SA', 0x1e1f20212223 )
            self.check_field( p4, 'L2_hdr[3].DA', 0x242526272829 )
            self.check_field( p4, 'L2_hdr[3].SA', 0x2a2b2c2d2e2f )
            self.check_field( p4, 'L2_hdr[4].DA', 0x303132333435 )
            self.check_field( p4, 'L2_hdr[4].SA', 0x363738393a3b )

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
    fields { number: 32 ; unused : 64;}
}

L2_def    L2_hdr;
meta_def  metadata  meta_hdr;

parser start  { extract ( L2_hdr ) ; 
                return GET_META ;
              }
parser GET_META  { set_metadata ( meta_hdr.number, 1234 ) ; 
                   return  P4_PARSING_DONE ; 
                 }
"""
        
        exp_bytes_used = 1*12
        pkt = [ i for i in range(12) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.DA', 0x102030405 )
            self.check_field( p4, 'L2_hdr.SA', 0x60708090a0b )
            self.check_field( p4, 'meta_hdr.number', 1234 )
            self.check_field( p4, 'meta_hdr.unused', None )

        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Unexpected Runtime Error:",err
            self.assert_(False)




    """ Test parser switch return ------------------------------------------------------------"""
    def test8(self, debug=1):

        program = """
header L2_def { fields { type0: 8; }    }
header L3_def { fields { jjj: 8;   }    }
header Type_0 { fields { type1: 8; }    }
header Type_1 { fields { four: 32; }    }

L2_def    L2_hdr;
L3_def    L3_hdr[3];
Type_0    Type_0_hdr;
Type_1    Type_1_hdr;

parser start  {
                extract ( L2_hdr    ) ; /* 0 */
                extract ( L3_hdr[0] ) ; /* 1 */
                extract ( L3_hdr[1] ) ; /* 2 */
                return switch ( current(4,12), latest.jjj, L2_hdr.type0, L3_hdr[1].jjj ) 
                /*                    304         02            00           02 = 12952141826*/
                { 0           : GET_TYPE0 ; 
                  1, 3 mask 7 : P4_PARSING_DONE ; 
                  12952141826 : GET_TYPE1 ;
                  default     : GET_TYPE0 ; 
                }
              }

parser GET_TYPE0 { extract ( Type_0_hdr ) ;
                   return  P4_PARSING_DONE ; 
                 }
parser GET_TYPE1 { extract ( Type_1_hdr ) ;
                   return  P4_PARSING_DONE ; 
                 }
"""
        
        exp_bytes_used = 7
        pkt = [ i for i in range(8) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.type0', 0x0 )
            self.check_field( p4, 'L3_hdr[0].jjj', 0x1 )
            self.check_field( p4, 'L3_hdr[1].jjj', 0x2 )
            self.check_field( p4, 'Type_1_hdr.four', 0x3040506 )

        except GP4.GP4_Exceptions.RuntimeError,err:
            print "Unexpected Runtime Error:",err
            self.assert_(False)







if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    single = unittest.TestSuite()
    single.addTest( test_dev('test5c' ))
    unittest.TextTestRunner().run(single)
