# GP4 Compiler Helper functions
#
## @package GP4


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
def print_syntax_err(err_msg, string, loc):
    print "Syntax Error:",err_msg
    show_source_loc(string, loc)

