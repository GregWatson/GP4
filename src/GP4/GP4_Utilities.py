# GP4_Utilities: GP4 Utility functions
#
## @package GP4

import GP4_Exceptions

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

    ## Create new Bits object
    # @param self: the new Bits object
    # @param bytes : [ integers ]
    def __init__(self, bytes):
        self.bytes = bytes[:]
        self.bits_left  = 8  # bits left in first byte.

    ## Return string of first few bytes as hex str
    # @param self: the new Bits object
    def first_few_bytes_as_hex_str(self):
        stop = 6 if len(self.bytes)>6 else -1
        hexL = [ "0x%02x" % b for b in self.bytes[0:stop] ]
        s = ' '.join(hexL)
        if len(self.bytes)>6: s+= '... (%d more)' % (len(self.bytes) - 6)
        return s
