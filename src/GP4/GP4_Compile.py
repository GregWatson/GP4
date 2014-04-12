# Top level compiler code.
# Given a parse tree, compile it.

import sys, copy
import GP4_Global
from GP4_Exceptions import *
from GP4_PyParse import *

class Compiler(object):

    def __init__(self, gbl):

        self.gbl = gbl

        #register compiler with the global object
        gbl.set_compiler(self)


    def compile_parse_tree(self, parse_tree, hier='', top_module=''):
        ''' Given a global object and a parse_tree (created by PyParsing)
            compile the parse tree and update the global object as needed.
            After compilation gbl should contain the initial event list
            and the database of all signals.
            gbl: global object
            parse_tree: from PyParsing
            hier: string indicating current module hierarchy.
            top_module: string. Name of top level module. else ''
        '''

        for el in parse_tree:
            print el


    ## Error handling routine.
    # @param self : object
    # @param *args : list of strings to be printed in the error message.
    # @return : None  ( executes sys.exit(1) )
    def error(self, *args):
        print "ERROR: VeriCompile:",
        for arg in args: print arg,
        print
        sys.exit(1)


## Compile a GP4 program given as a single string.
# @param program : string. The GP4 program
# @param debug : debug vector integer
# @param opt_vec : options vector integer
# @param sim_end_time_fs : integer. Sim end time in fs
# @param top_module : string. Name of top level module. (or '')
# @return gbl object or None if error
def compile_string_as_string(program, debug=0, opt_vec=0, sim_end_time_fs=100000,top_module=''):
    ''' This is a helper function '''

    if debug:
        print program

    parser = new_GP4_parser()
    try:
        parsed_data = parser.parseString(program, True)

    except ParseException, err:
        print "err.line is ",err.line
        print "col is ", err.column
        text_lines = err.line.split(';')
        line_num = 0
        char_count = 0
        last_line  = None
        print_next_line  = False
        for line in text_lines:
            line += ';'
            line_num += 1
            if print_next_line:
                print "[%3d] %s" % (line_num, line)
                break    
            if ( char_count + len(line) ) >= err.column:
                if last_line: print "[%3d] %s" % (line_num-1, last_line)
                print "[%3d] %s" % (line_num, line)
                print "      " + " "*(err.column-char_count-1) + "^"
                print_next_line  = True
            else: 
                last_line = line
                char_count +=  len(line)

        print err
        return None

    # need Global gbl for tracking all signals and events
    gbl = GP4_Global.Global( debug = debug )  


    # Compile the parse tree

    compiler = Compiler( gbl )
    compiler.compile_parse_tree( parsed_data )

    return gbl




