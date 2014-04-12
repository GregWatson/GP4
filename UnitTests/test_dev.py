##################################################
#
# test_dev.py - development tests
#
##################################################

import sys, unittest
sys.path.append("/home/gwatson/Work/GP4/src")
try:
    from GP4.GP4_PyParse import *
    import GP4.GP4_Compile
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
    gbl = GP4.GP4_Compile.compile_string_as_string(
            program=program, 
          )

    if not gbl:
        print "Hmmm. Syntax error?"
        sys.exit(1)

    # run sim

    gbl.run_sim(debug)
    return gbl

    
class test_dev(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self):pass
    

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
"""
        gbl = simple_test(data, debug=debug)


if __name__ == '__main__':
    # unittest.main()
    # can run all tests in dir via:
    #        python -m unittest discover

    single = unittest.TestSuite()
    single.addTest( test_dev('test1' ))
    unittest.TextTestRunner().run(single)
