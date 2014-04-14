# GP4_Utilities: GP4 Utility functions
#
## @package GP4

import GP4_Exceptions
import sys

## print the surrounding text where the syntax error occurred.
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @return None
def show_source_loc(string, loc):
    text_lines = string.split('\n')
    line_num = 0
    char_count = 0
    last_line  = None
    print_next_line  = False
    for line in text_lines:
        line_num += 1
        if print_next_line:
            print "%3d: %s" % (line_num, line)
            break    
        if ( char_count + len(line) ) >= loc:
            if last_line: print "%3d: %s" % (line_num-1, last_line)
            print "%3d: %s" % (line_num, line)
            print "      " + " "*(loc-char_count-1) + "^"
            print_next_line  = True
        else: 
            last_line = line
            char_count +=  len(line)

    return None

## print a syntax error message
# @param err_msg : String.  The error string
# @param string : String.  Source text
# @param loc    : Integer. location in text of this object
# @return None
def print_syntax_err(err_msg, string='', loc=0):
    print "Syntax Error:",err_msg
    if string: show_source_loc(string, loc)
    raise GP4_Exceptions.SyntaxError('')


# Bits class. Behaves as an ordered sequence of bits.

class Bits(object):

    bits_mask = [ 0, 0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f, 0x7f, 0xff ]

    ## Create new Bits object
    # @param self: the new Bits object
    # @param bytes : [ integers ]
    def __init__(self, bytes):
        self.bytes = bytes[:]
        self.bits_left  = 8  # bits left in first byte.

    ## Extract num_to_get bits from the bytes array and return as integer.
    # @param self: Bits object
    # @param num_to_get : integer
    # @return (err, extracted_bits) err=string,  extracted_bits=integer
    def get_next_bits(self, num_to_get):
        if num_to_get == 0:
            return ('Bits:get_next_bits: number ot get is zero!',0)

        if len(self.bytes) == 0:
            return ('Bits:get_next_bits: no bytes left!',0)

        total_remaining_bits = self.bits_left + 8*(len(self.bytes)-1)
        if num_to_get > total_remaining_bits:
            return ('Bits:get_next_bits: needed %d bits but only %d left!'
                    % (num_to_get,total_remaining_bits) ,0)

        extracted_bits = 0

        while num_to_get >= self.bits_left:

            num_to_get    -= self.bits_left
            extracted_bits = ( extracted_bits << self.bits_left ) | self.pop(self.bits_left)

        if num_to_get:
            assert(num_to_get < 8)
            extracted_bits = ( extracted_bits << num_to_get ) | self.pop(num_to_get)

        return ('', extracted_bits)


    ## Extract 1-8 bits from first byte. Remove it if we take all.
    # @param self: Bits object
    # @param num_to_get : integer
    # @return extracted_bits
    def pop(self, num_to_get):
        """ It's an error to try to pop more bits than are left """
        if num_to_get > self.bits_left:
            print "Bits:pop(): trying to pop",num_to_get,"bits but only",self.bits_left," left."
            sys.exit(1)

        self.bits_left -= num_to_get
        extracted_bits = self.bytes[0] >> self.bits_left

        if self.bits_left == 0:
            del self.bytes[0]
            if len(self.bytes): self.bits_left = 8
        else:
            self.bytes[0] &= Bits.bits_mask[self.bits_left]

        return extracted_bits

        

    ## Return string of first few bytes as hex str
    # @param self: the new Bits object
    def first_few_bytes_as_hex_str(self):
        stop = 6 if len(self.bytes)>6 else -1
        hexL = [ "0x%02x" % b for b in self.bytes[0:stop] ]
        s = ' '.join(hexL)
        if len(self.bytes)>6: s+= '... (%d more)' % (len(self.bytes) - 6)
        return s
