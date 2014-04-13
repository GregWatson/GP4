##################################################
#
# test_dev.py - development tests
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Work/GP4/src")
try:
    from GP4.GP4_CompilerHelp import compile_string
    import GP4.GP4_Exceptions
except ImportError, err:
    print "Unable to load GP4 libs. sys.path is:"
    for p in sys.path: print "\t",p
    print err

## Compile and run a GP4 program provided as a string.
# @param program : String.  The program.
# @param debug   : Integer. Debug flags

def simple_test(program, debug=0):
    ''' Given a string (GP4 program) in program, compile and run it.
    '''
    p4 = compile_string( program=program )

    if not p4:
        print "Hmmm. Syntax error?"

    return p4

    
class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass
    

    """ Test header decl and header insts  -----------------------------------------"""
    def test1(self, debug=1):

        data = """

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
        p4 = simple_test(data, debug=debug)


    """ Test syntax error handling ---------------------------------------------------"""
    def test2(self, debug=1): 

        data = """ header vlan_tag { }"""
        try:
            p4 = simple_test(data, debug=debug)
        except GP4.GP4_Exceptions.SyntaxError,err:
            print "Syntax Error was expected"


    """ Test parser funcs ------------------------------------------------------------"""
    def test3(self, debug=1):

        data = """
parser we_are_done { return P4_PARSING_DONE ; }
parser nxt_is_done { return we_are_done ; }
parser prsr_switch { return switch ( L2.DA ) { 1 : nxt_state ; } }
/* 
parser prsr_switch { return switch ( L2.DA, L2.SA ) { 
                        12 : nxt_is_done; 
                        5, 9 : five_or_nine;
                        800 mask 22 : masked_state; 
                     } }
*/
"""
        p4 = simple_test(data, debug=debug)





if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    single = unittest.TestSuite()
    single.addTest( test_dev('test3' ))
    unittest.TextTestRunner().run(single)
