# GP4_Packet_Parser.py - runtime packet parser.
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

    while state != 'P4_PARSING_DONE':
        
        print "step: [%s] pkt=[%s]" % (state, bits.first_few_bytes_as_hex_str())

        parse_func = p4.get_parse_function(state)
        if not parse_func:
            return ('Parse function (state) "%s" not found' % state, bytes_used)

        (err, bytes_used, state) = parse_func.execute( p4, bits)

    return (err, bytes_used)
