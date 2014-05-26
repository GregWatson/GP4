# GP4_Packet_Parser.py - runtime packet parser.
#
# This will actually parse a packet and populate the header instances 
# as determined by the parser functions.
#
## @package GP4

from GP4_Utilities import print_syntax_err
from GP4_Utilities import Bits
import GP4_Exceptions
import sys

## Given a P4 object and a packet, parse the packet: i.e. create and populate the headers.
# @param p4  : P4 object
# @param pkt : [ bytes ]
# @return (err, bytes_used) : (err !=None if error), bytes_used = number of bytes consumed from header.

def parse_packet(p4, pkt, init_state):

    err = None
    bytes_used = 0
    bits = Bits(pkt)  # create bit stream from packet

    assert len(pkt),"pkt was empty - cannot parse."

    state = init_state
    p4.initialize_packet_parser() 

    while state != 'P4_PARSING_DONE':
        
        print "step: [%s] pkt=[%s]" % (state, bits.first_few_bytes_as_hex_str())

        parse_func = p4.get_parse_function(state)
        if not parse_func:
            raise  GP4_Exceptions.RuntimeError , 'Parse function (state) "%s" not found' % state

        (err, new_bytes_used, state) = parse_func.execute( p4, bits)

        bytes_used += new_bytes_used
        if err: 
            raise  GP4_Exceptions.RuntimeError, err


    print "After parsing, the following headers are defined:"
    for h in p4.hdr_extraction_order:
        if h.fields_created:
            print '  ',h

    print "The following metadata headers are created:"
    for h in p4.header_insts.values():
        if h.fields_created and h.hdr_is_metadata:
            print '  ',h

    return (err, bytes_used)
