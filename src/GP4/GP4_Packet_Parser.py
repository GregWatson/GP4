# GP4_Packet_Parser.py - runtime packet parser.
#
# This will actualy parse a packet and populate the header instances 
# as determined by the parser functions.
#
## @package GP4

from GP4_Utilities import print_syntax_err
from GP4_Utilities import Bits
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
            return ('Parse function (state) "%s" not found' % state, bytes_used)

        (err, new_bytes_used, state) = parse_func.execute( p4, bits)

        bytes_used += new_bytes_used
        if err: return (err, bytes_used)


    print "After parsing, the following headers are defined:"
    for h in p4.hdr_extraction_order:
        if h.is_valid:
            print h

    return (err, bytes_used)
