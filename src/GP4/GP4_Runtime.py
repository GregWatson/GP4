# GP4_Runtime.py - runtime system. Requires a P4 context to run with.
#
## @package GP4

from GP4_Utilities import print_syntax_err, show_source_loc
from GP4_Utilities import Bits
from pyparsing import ParseException
#from GP4_P4        import P4
import GP4_Exceptions
import GP4_Runtime_PyParse
import sys


class Runtime(object):

    ## Constructor for a Runtime object
    # @param self : New Runtime object
    # @param p4   : P4 object
    # @return self
    def __init__(self, p4):

        self.p4 = p4
        self.p4.load_default_actions()
        self.runtime_parser = None


    ## Parse a text cmd (string) supplied by user 
    # @param self : Runtime object
    # @param cmd  : String cmd
    # @return parsed_data  - PyParsing object from GP4_Runtime_PyParse
    def parse_cmd(self, cmd):
        print "Runtime parse cmd:",cmd

        if not self.runtime_parser:
            self.runtime_parser = GP4_Runtime_PyParse.new_GP4_runtime_parser()

        try:
            parsed_data = self.runtime_parser.parseString(cmd, True)

        except ParseException as err:

            show_source_loc(err.line, err.column)
            raise GP4_Exceptions.SyntaxError, "Syntax error line %s  column %s" % (str(err.line), str(err.column))

        # Compile the parse tree

        return parsed_data





    ## Execute a runtime cmd such as setting a table default value
    # @param self : Runtime object
    # @param cmd  : runtime cmd
    # @return None
    def run_cmd(self, cmd):
        ''' Process a parse tree object created by the PyParsing parser.
            First element is the string name of the cmd type.
            Uses the dir(self) introspection to find the function named like the cmd.
            Then invoke that function on the remainder of the parse tree object.
        '''
        print "Runtime: executing cmd:",cmd

        parse_tree = self.parse_cmd(cmd)
        print "Runtime: parse tree is", parse_tree

        obj_type_str = 'do_' + parse_tree[0][0]
        if obj_type_str not in dir(self):
            s = "Syntax error: run_cmd: unknown runtime command <%s>\n" %  parse_tree[0]
            s += "(No method %s). Parse list is:\n" % obj_type_str
            s += str(parse_tree)
            raise GP4_Exceptions.SyntaxError(s)

        getattr(self, obj_type_str)(*parse_tree[0][1:])




    ## Execute a table_op cmd. 
    # @param self : Runtime object
    # @param cmd  : Pyparse object for table_op
    # Return None
    def do_table_op( self, tbl_name, tbl_method, *args):
        print "called",tbl_name,".",tbl_method,"(",args,")"
        tbl = self.p4.get_table(tbl_name)
        if not tbl:
            raise GP4_Exceptions.RuntimeError, "Unknown table '%s'" % tbl_name
        
        getattr(tbl, tbl_method)(*args)



    ## Parse a packet: i.e. create and populate the headers in our attached P4 object
    # @param self: Runtime object
    # @param pkt : [ bytes ]
    # @param init_state : start state for parser
    # @return (err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.
    def parse_packet(self, pkt, init_state='start'):

        err = None
        bytes_used = 0
        bits = Bits(pkt)  # create bit stream from packet

        assert len(pkt),"pkt was empty - cannot parse."

        state = init_state
        self.p4.initialize_packet_parser() 

        while state != 'P4_PARSING_DONE':

            print "step: [%s] pkt=[%s]" % (state, bits.first_few_bytes_as_hex_str())

            parse_func = self.p4.get_parse_function(state)
            if not parse_func:
                raise  GP4_Exceptions.RuntimeError , 'Parse function (state) "%s" not found' % state

            (err, new_bytes_used, state) = parse_func.execute( self.p4, bits)

            bytes_used += new_bytes_used
            if err: 
                raise  GP4_Exceptions.RuntimeError, err


        print "After parsing, the following headers are defined:"
        for h in self.p4.hdr_extraction_order:
            if h.fields_created:
                print '  ',h

        print "The following metadata headers are created:"
        for h in self.p4.header_insts.values():
            if h.fields_created and h.hdr_is_metadata:
                print '  ',h

        return (err, bytes_used)
