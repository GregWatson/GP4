# GP4_Utilities: GP4 Utility functions
#
## @package GP4

import GP4_Exceptions
import sys


## COnvert string to integer. String may be hex (startswith 0x)
# @param string : String 
# @return integer
def get_integer(string):
    if type(string) == type(1): return string 
    if string.startswith('0x'): return int(string[2:],16)
    else: return int(string)

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
    raise GP4_Exceptions.SyntaxError, ''

## Convert hdr ref PyParsing object to string
# @param hdr_ref : PyParsing object
# @return String
def hdr_ref_to_string(hdr_ref):
    """ hdr ref is list of length 1 or 2 """
    if len(hdr_ref)==1: return hdr_ref[0]
    else:
        assert len(hdr_ref)==2
        return "%s[%s]" % (hdr_ref[0], hdr_ref[1])

## Convert field ref PyParsing object to string
# @param field_ref : PyParsing object
# @return String
def field_ref_to_string(field_ref):
    """ field ref is list of length 2: hdr_ref and field_name """
    assert len(field_ref)==2
    return  hdr_ref_to_string(field_ref[0]) + "." + field_ref[1]



## Given list of strings or lists of strings, etc., flatten it to a string.
# @param expr : list of strings or more lists of strings
# @returns String
def flatten_list_of_strings( expr):
    if type(expr) == type('s'): 
        return expr
    else:
        if len(expr)==1: 
            return flatten_list_of_strings(expr[0])
        code = '('
        for el in expr: 
            code += ' ' + flatten_list_of_strings(el)
        return code + ' )'

## Given a pyparsing field_ref object, return hdr_name, hdr_index and field_name
# @param field_ref : pyparsing field_ref object
# @returns ( hdr_name, hdr_index ,field_name ) hdr_index='' if none
def get_hdr_hdr_index_field_name_from_field_ref(field_ref):
    """ field_ref is like: [['L3_hdr', '0'], 'stuff']
                       or: [['L3_simple'], 'stuff']
    """
    assert len(field_ref)==2,"Expected fieldref object of length 2. saw %s" % `field_ref`
    field_name = field_ref[1]
    hdr_ref    = field_ref[0]
    hdr_name   = hdr_ref[0]
    hdr_index  = '' if len(hdr_ref)==1 else hdr_ref[1]
    return ( hdr_name, hdr_index ,field_name )

# Bits class. Behaves as an ordered sequence of bits.

class Bits(object):

    bits_mask = [ 0, 0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f, 0x7f, 0xff ]

    ## Create new Bits object
    # @param self: the new Bits object
    # @param bytes : [ integers ]
    def __init__(self, bytes):
        self.bytes = bytes[:]
        self.bits_left = 8 if len(self.bytes) else 0  # bits left in first byte.


    ## Copy Bits object
    # @param self: the original Bits object
    # @return copy of self
    def copy(self):
        new = Bits([])
        new.bytes     = self.bytes[:]
        new.bits_left = self.bits_left
        return new


    ## Extract num_to_get bits from the bytes array and return as integer.
    # @param self: Bits object
    # @param num_to_get : integer
    # @return (err, extracted_bits) err=string,  extracted_bits=integer
    def get_next_bits(self, num_to_get):
       
        if num_to_get == 0:
            return ('Bits:get_next_bits: number to get is zero!',0)

        if len(self.bytes) == 0:
            return ('Bits:get_next_bits: no bytes left!',0)

        total_remaining_bits = self.bits_left + 8*(len(self.bytes)-1)
        if num_to_get > total_remaining_bits:
            return ('Bits:get_next_bits: needed %d bits but only %d left!'
                    % (num_to_get,total_remaining_bits) ,0)

        extracted_bits = 0

        while num_to_get and num_to_get >= self.bits_left:

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

        assert  (num_to_get > 0 and num_to_get <= 8), \
                "ERROR: Trying to pop %d bits. Must be 1-8." % num_to_get

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

        
    ## Extract bit_width bits non-destructively, starting from bit_offset
    # @param self: Bits object
    # @param bit_offset : integer
    # @param bit_width  : integer
    # @return extracted_bits: Integer
    def get_bit_field(self, bit_offset, bit_width):
        tmp = self.copy()
        if bit_offset: # discard bit_offset bits
            (err, extracted_bits) = tmp.get_next_bits(bit_offset)
        (err, extracted_bits) = tmp.get_next_bits(bit_width)
        return extracted_bits



    ## Return string of first few bytes as hex str
    # @param self: the new Bits object
    def first_few_bytes_as_hex_str(self):
        stop = 6 if len(self.bytes)>6 else -1
        hexL = [ "0x%02x" % b for b in self.bytes[0:stop] ]
        s = ' '.join(hexL)
        if len(self.bytes)>6: s+= '... (%d more)' % (len(self.bytes) - 6)
        return s


# Match_Key class. Used by tables to perform a match operation.
# Created from the actual header fields of a packet.
class Match_Key(object):

    ## Create new Match_Key object
    # @param self: the new Match_Key object
    # @param value: Integer.  actual binary value of this match key
    # @param length: Integer.  how many lsb are valid. may be 0 if field is invalid
    # @param valid: Boolean.   Whether value and length for this Match_Key are valid.
    def __init__(self, value=None, length=0, valid=False):
        self.value  = value    # Integer; actual binary value of this match key
        self.length = length   # Integer; how many lsb are valid. may be 0 if field is invalid
        self.valid  = valid    # Boolean; whether key is valid

    ## Create string for Match Key
    # @param self: the new Match_Key object
    # @return String
    def __str__(self):
        if not self.valid: return 'invalid'
        else: return 'val=0x%x len=%0d' % (self.value, self.length)


# Match_Val class. ########################################################
# One or more Match_Vals are used to define the value of the entry that is matched against.
class Match_Val(object):

    ## Create new Match_Val object
    # @param self: the new Match_Val object
    # @param value: Integer.  actual binary value of this match key
    # @param mask:  Integer.   If Ternary, mask to apply to match key else None
    # @param valid: Boolean.   Whether other fields for this Match_Val are valid.
    def __init__(self, value=None, mask=None, valid=False):

        self.value  = value    # Integer; actual binary value of this Match_Val
        self.mask   = mask     # Integer; If Ternary, mask to apply to match key else None
        self.valid  = valid    # Boolean; whether other fields are valid

    ## Return True if entry matches the given Match_Key
    # @param self: Match_Val object
    # @param match_key : Match_Key
    # @return Boolean
    def matches(self, match_key):
        if not self.valid: return False
        if not match_key.valid: return False

        if self.mask != None: # Ternary.
            return match_key.value & self.mask == self.value
        
        return  match_key.value == self.value 


    def __str__(self):
        if not self.valid: return 'not valid'
        s = "val=0x%x" % self.value
        if self.mask != None: s += " mask=0x%x" % self.mask
        return s




# Table Entry class ####################################################
class Entry(object):

    ## Create new Entry object
    # @param self: the new Entry object
    # @return self
    def __init__(self):
        self.matchList = []
        self.action    = None


    ## Set matchList field to given [ Match_Val ]
    # @param self: the Entry object
    # @param matchList :  [ Match_Val ]
    # @return None
    def set_matchList(self, matchList=[]):
        print 'set_matchList: [', 
        for e in matchList: print e,',',
        print ']'
        self.matchList = matchList

    ## Set action field to given action
    # @param self: the Entry object
    # @param action : pyparsing action_stmt
    # @return None
    def set_action(self, action=[]):
        print 'set_action:', action
        self.action = action

    ## Get action field to given action
    # @param self: the Entry object
    # @return  Action
    def get_action(self):
        return self.action


    ## Create the list of Match_Val objects and Create new Entry object
    # @param self: the new Entry object
    # @param entry_list : pyparse list of either number or tuple(num,num)
    # @return [ Match_Val ]
    def make_match_vals_from_pyparse(self, entry_list):
        print "make_match_vals_from_pyparse", entry_list
        L = []
        for e in entry_list:
            if type(e) == type('s'): # simple integer 
                v = get_integer(e)
                L.append(Match_Val(value=v, valid=True))
            else:
                assert len(e)==2 # Tuple of (value, mask)
                v,m = get_integer(e[0]), get_integer(e[1])
                L.append(Match_Val(value=v, mask=m,valid=True))
        return L


    ## Return True if entry matches the given list of match_keys
    # @param self: the Entry object
    # @param  match_keys : [ Match_Key ]
    # @return Boolean
    def matches(self, match_keys=[]):
        if len(match_keys) != len(self.matchList): return False
        for (ix, ml) in enumerate(self.matchList):
            if not ml.matches(match_keys[ix]): return False
        return True

