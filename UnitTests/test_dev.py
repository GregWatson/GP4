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
    actions { add_to_field ; }
    min_size 23;
    max_size 1024;
}

"""
        setup_cmds  = ['my_table.set_default_action( add_to_field ( L3_hdr[0].stuff, 1 ))'] 

        exp_bytes_used = 4
        pkts = [[ i for i in range(exp_bytes_used)]]

        try:
            (p4, err, num_bytes_used ) = setup_tables_parse_and_run_test(
                    program, 
                    setup_cmds,              # List of Runtime cmds
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L3_hdr[0].stuff', 0x10204)
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
L3_def L3_simple;

parser start  { extract ( L3_hdr[next] ); 
                return P4_PARSING_DONE ; }

control ingress { 
    apply_table( my_table );
}

table my_table { 
    reads { L3_hdr[0].stuff : exact ; 
            L3_hdr[0].stuff mask 0xff : ternary ; 
            L3_simple.stuff mask 0xff : lpm ; 
    }
    actions { add_to_field ; }
    min_size 1;
}


"""
        setup_cmds  = ['my_table.set_default_action( add_to_field ( L3_hdr[0].stuff, -1 ))'] 

        exp_bytes_used = 4
        pkts = [[ i for i in range(exp_bytes_used)]]

        try:

            (p4, err, num_bytes_used ) = setup_tables_parse_and_run_test(
                    program, 
                    setup_cmds,              # List of Runtime cmds
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw parse runtime err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'L3_hdr[0].stuff', 0x10202)
            self.check_table( p4, 'my_table', min_size=1)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)

    """ Test table add_to_field action with two fields ----------------------------------------"""
    def test202(self, debug=1):

        program = """
header Hop_count_def { fields { count : 32; }  }

Hop_count_def  hop_count_hdr[2];

parser start  { extract ( hop_count_hdr[next] ) ; 
                extract ( hop_count_hdr[next] ) ; 
                return P4_PARSING_DONE ; }

control ingress { 
    apply_table( my_table );
}

table my_table { 
    actions { add_to_field ; } 
}

"""

        setup_cmds  = ['my_table.set_default_action( add_to_field ( hop_count_hdr[0].count, hop_count_hdr[1].count ))'] 

        exp_bytes_used = 8
        pkts = [ [ i for i in range(exp_bytes_used) ] ]

        try:

            (p4, err, num_bytes_used ) = setup_tables_parse_and_run_test(
                    program, 
                    setup_cmds,              # List of Runtime cmds
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'hop_count_hdr[0].count', 0x406080a) # 0x10203 + 0x4050607
            self.check_field( p4, 'hop_count_hdr[1].count', 0x4050607)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data


    """ Test runtime adding a table entry and then matching on it -------------------------------"""
    def test203(self, debug=1):

        program = """
header Hop_count_def { fields { type: 8 ; count : 32; }  }

Hop_count_def  hop_count_hdr;

parser start  { extract ( hop_count_hdr ) ; 
                return P4_PARSING_DONE ; }

control ingress { 
    apply_table( my_table );
}

table my_table { 
    reads { hop_count_hdr.type : exact ; }
    actions { add_to_field ; } 
}

"""
        #                                     tuple( match, action ) 
        setup_cmds  = [  'my_table.set_default_action( add_to_field ( hop_count_hdr.count, 1 ))' ,
                         'my_table.add_entry( any, [5], add_to_field ( hop_count_hdr.count, hop_count_hdr.type ) )'
                      ] 

        exp_bytes_used = 5
        pkts = [ [ i+5 for i in range(exp_bytes_used) ] ]

        try:

            (p4, err, num_bytes_used ) = setup_tables_parse_and_run_test(
                    program, 
                    setup_cmds,              # List of Runtime cmds
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'hop_count_hdr.type', 0x5) 
            self.check_field( p4, 'hop_count_hdr.count', 0x607080e)

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data




    """ Test next_table -------------------------------"""
    def test204(self, debug=1):

        program = """
header T1_def { fields { type: 8 ; }  }
header T2_def { fields { type: 8 ; }  }

T1_def T1;
T2_def T2;

parser start  { extract ( T1 ) ; extract ( T2 ) ; 
                return P4_PARSING_DONE ; }

control ingress { 
    apply_table( table1 );
}

table table1 { 
    reads { T1.type : exact ; }
    actions { add_to_field next_table table2; } 
}

table table2 { 
    reads { T2.type : exact; }
    actions { add_to_field; } 
}

"""
        #                
        setup_cmds  = [  
                         'table1.add_entry( any, [5], add_to_field( T1.type, 5)  )',
                         'table2.add_entry( any, [6], add_to_field( T2.type, 22) )'
                      ] 

        exp_bytes_used = 2
        pkts = [ [ i+5 for i in range(exp_bytes_used) ] ]

        try:

            (p4, err, num_bytes_used ) = setup_tables_parse_and_run_test(
                    program, 
                    setup_cmds,              # List of Runtime cmds
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'T1.type', 0xa) 
            self.check_field( p4, 'T2.type', 28) 

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data




    """ Test 'reads' with a 'valid' field -------------------------------"""
    def test205(self, debug=1):

        program = """
header T1_def { fields { type: 8 ; }  }
header T2_def { fields { type: 8 ; }  }

T1_def T1;
T2_def T2;

parser start  { extract ( T1 ) ; 
                return switch (T1.type ) 
                { 5           : GET_T2 ; 
                  default     : P4_PARSING_DONE ; 
                }
              }
parser GET_T2 { extract ( T2 ); 
                return  P4_PARSING_DONE ; 
              }    

control ingress { 
    apply_table( table1 );
}

table table1 { 
    reads { T1.type : valid ; }
    actions { no_action next_table table2; } 
}

table table2 { 
    reads { T2.type : valid ; }
    actions { add_to_field; } 
}

"""

        p4, runtime = create_P4_and_runtime(program)

        #                
        setup_cmds  = [  
                         'table1.add_entry( any, [1], no_action() )',
                         'table2.add_entry( 1, [1], add_to_field( T2.type, 22) )'
                      ] 
        run_cmds( p4, runtime, setup_cmds )

        exp_bytes_used = 2
        pkts = [ [ i+5 for i in range(exp_bytes_used) ] ]

        try:

            (err, num_bytes_used ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'T1.type', 0x5) 
            self.check_field( p4, 'T2.type', 28) 

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data


        # Now put in a packet with an unparsed (invalid) T2  (T1.type is not 5)

        exp_bytes_used = 1
        pkts = [ [ i for i in range(exp_bytes_used) ] ]

        try:

            (err, num_bytes_used ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'T1.type', 0x0) 


        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data


        print"\n\n---- Now add an entry that matches on an invalid T2 and adjusts T1.type\n\n"

        # Now add an entry that matches on an invalid T2 and adjusts T1.type
        setup_cmds  = [  
                         'table2.add_entry( 2, [0], add_to_field( T1.type, 100) )'
                      ] 
        run_cmds( p4, runtime, setup_cmds )

        exp_bytes_used = 1
        pkts = [ [ 0 for i in range(exp_bytes_used) ] ]

        try:

            (err, num_bytes_used ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                    # List of packets
                    init_state='start',      # parser
                    init_ctrl='ingress',     # control program start
                    debug=debug)

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'T1.type', 100) 

        except GP4.GP4_Exceptions.RuntimeError as err:
            print "Unexpected Runtime Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.InternalError as err:
            print "Unexpected Internal Error:",err.data
            self.assert_(False)
        except GP4.GP4_Exceptions.SyntaxError as ex_err:
            print "Unexpected SyntaxError:", ex_err.data




    """ Test multiple actions -------------------------------"""
    def test206(self, debug=1):

        program = """
header T1_def { fields { type: 8 ; }  }
header T2_def { fields { type: 8 ; }  }
header T3_def { fields { type: 8 ; }  }

T1_def T1;
T2_def T2;
T3_def T3;

parser start  { extract ( T1 ) ;  extract ( T2 ) ;  extract ( T3 ) ;  return P4_PARSING_DONE ; }

control ingress { 
    apply_table( table1 );
}

table table1 { 
    actions { add_T1_to_T2_and_T3 ; } 
}

action add_T1_to_T2_and_T3( a_field, b_field) { 

    add_to_field(T2.type, a_field) ; 
    add_to_field(T3.type, b_field) ; 
}

"""

        try:
            p4, runtime = create_P4_and_runtime(program)

            setup_cmds  = ['table1.set_default_action( add_T1_to_T2_and_T3( T1.type, T1.type ) )'] 
            run_cmds( p4, runtime, setup_cmds )

            #                
            exp_bytes_used = 3
            pkts = [ [ i+5 for i in range(exp_bytes_used) ] ]

            (err, num_bytes_used ) = process_pkts(
                    p4,
                    runtime,
                    pkts,                       # List of packets
                    init_state = 'start',       # parser start state
                    init_ctrl  = 'ingress',     # control program start
                    debug=debug )

            self.assert_( err=='', 'Saw err:' + str(err) )
            self.assert_( num_bytes_used == exp_bytes_used, 
                      'Expected %d bytes consumed, Saw %d.' % (exp_bytes_used, num_bytes_used ))
            self.check_field( p4, 'T1.type', 0x5) 
            self.check_field( p4, 'T2.type', 11) 
            self.check_field( p4, 'T3.type', 12) 

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
        single.addTest( test_dev('test206' ))
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
