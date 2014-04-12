# Global object
# used in parsing and run time (simulation)

import GP4_Exceptions
import datetime, sys

class Global(object):

    # Debug values (bit vector)
    DBG_STATS      = 1<<1
    DBG_EVENT_LIST = 1<<2

    def __init__(self, debug=0):

        self.compiler   = None # ref to Compiler object (gets set when Compiler created)

    ## Register a Compiler object with the global object.
    # @param self : Global object
    # @param compiler : Compiler object
    # @return None
    def set_compiler(self, compiler):
        self.compiler = compiler


    def run_sim(self, debug=0):
        print "Running simulation..."
        print "Done."

    ## Create printable string for Global object
    # @param self : Global object
    # @return String 
    def __str__(self):
        s = 'Global data'
        return s
