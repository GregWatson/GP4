# GP4_Runtime.py - runtime system. Requires a P4 context to run with.
#
## @package GP4

from GP4_Utilities import print_syntax_err
from GP4_Utilities import Bits
#from GP4_P4        import P4
import GP4_Exceptions
import sys


class Runtime(object):

    ## Constructor for a Runtime object
    # @param self : New Runtime object
    # @param p4   : P4 object
    # @return self
    def __init__(self, p4):

        self.p4 = p4        

        # run time fields per processed packet 
        self.hdr_extraction_order = []  # list of header objects in the order they were extracted.
        self.latest = None  # latest extracted header in a parser function.



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
