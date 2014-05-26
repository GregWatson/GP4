##################################################
#
# test_dev_parse.py - development tests
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
        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Runtime Error",err.data,"was expected"



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
        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Runtime Error was expected."
            print err.data



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
        except GP4.GP4_Exceptions.RuntimeError as ex_err:
            print "Runtime Error was expected:", ex_err.data




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
            print "test5c: SyntaxError was expected:", ex_err.args




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

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
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

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
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

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)



    """ Test parser switch return default ---------------------------------------------"""
    def test8a(self, debug=1):

        program = """
header L2_def  { fields { type0: 8; }    }
header bad_def { fields { jjj: 8;   }    }
header Type_1  { fields { four: 32; }    }

L2_def    L2_hdr;
bad_def   bad_hdr;
Type_1    Type_1_hdr;

parser start  {
                extract ( L2_hdr    ) ; /* 5 */
                return switch ( L2_hdr.type0 ) 
                { 0,1,2,3,4, 6,7,8,9,10 : BAD ; 
                  default               : GET_NEXT4 ; 
                }
              }

parser BAD { extract ( bad_hdr ) ;
                   return  BAD ; 
           }
parser GET_NEXT4 { extract ( Type_1_hdr ) ;
                   return  P4_PARSING_DONE ; 
                 }
"""
        
        exp_bytes_used = 5
        pkt = [ 5+i for i in range(8) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.type0', 0x5 )
            self.check_field( p4, 'Type_1_hdr.four', 0x6070809 )

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)




    """ Test parser switch return default ---------------------------------------------"""
    def test8b(self, debug=1):

        program = """
header L2_def  { fields { type0: 8; }    }
header bad_def { fields { jjj: 8;   }    }
header Type_1  { fields { four: 32; }    }

L2_def    L2_hdr;
bad_def   bad_hdr;
Type_1    Type_1_hdr;

parser start  {
                extract ( L2_hdr    ) ; /* 5 */
                return switch ( L2_hdr.type0 ) 
                { 4 mask 6 : SECOND ; 
                  default  : BAD   ; 
                }
              }

parser BAD { extract ( bad_hdr ) ;
                   return  BAD ; 
           }
parser SECOND { extract ( Type_1_hdr ) ;
                return  P4_PARSING_DONE ; 
              }
"""
        
        exp_bytes_used = 5
        pkt = [ 5+i for i in range(8) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.type0', 0x5 )
            self.check_field( p4, 'Type_1_hdr.four', 0x6070809 )

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)




    """ Test use of length "*" in header decl  ---------------------------------------------"""
    def test9(self, debug=1):

        program = """
header L2_def  { fields { len: 8;
                          other: 16; 
                          data: *;
                        }
                 length (len * 2)>>1 + 1 - 1 ;
                 max_length 10;
               }  

L2_def    L2_hdr;

parser start  {
                extract ( L2_hdr ) ; 
                return  P4_PARSING_DONE ; 
              }
"""
        
        exp_bytes_used = 10
        pkt = [ 10+i for i in range(10) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L2_hdr.len', 10 )
            self.check_field( p4, 'L2_hdr.other', 0xb0c )
            self.check_field( p4, 'L2_hdr.data', 0xd0e0f10111213 )

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.RuntimeParseError as err:
            print "Unexpected Runtime Parse Error:",err.data
            self.assert_(False)



    """ Test use of length "*" in header decl  ---------------------------------------------"""
    def test9a(self, debug=1):

        program = """
header L2_def  { fields { len: 8;
                          other: 16; 
                          data: *;
                        }
                 length (len * 2)>>1 + 1 - 1 ;
                 max_length 1;
               }  

L2_def    L2_hdr;

parser start  {
                extract ( L2_hdr ) ; 
                return  P4_PARSING_DONE ; 
              }
"""
        
        exp_bytes_used = 10
        pkt = [ 10+i for i in range(10) ]

        try:

            (p4, err, num_bytes_used ) = parse_and_run_test(program, pkt, init_state='start', 
                                                        debug=debug)
            self.assert_( False )  # should have exception raised

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.RuntimeParseError as err:
            print "Good: Expected Runtime Parse Error:",err.data
            self.assert_(True)







if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    if (True):
        single = unittest.TestSuite()
        single.addTest( test_dev('test9' ))
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
