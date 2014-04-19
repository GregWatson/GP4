# P4  object - contains structures compiled from a P4 program
#
## @package GP4

from GP4_Utilities import print_syntax_err
import GP4_Exceptions
import sys

class P4(object):

    ## Constructor for P4 object
    # @param self : New P4 object
    # @return self
    def __init__(self):

        self.header_decls = {} # maps name of header_decl to header_decl object
        self.header_insts = {} # maps inst name of header_inst to header_inst or header_stack object
        self.parser_functions = {} # maps parser function name (string) to parse function object


        # run time fields
        self.hdr_extraction_order = []  # list of header objects in the order they were extracted.

    ## Add a new object (e.g. header_decl) to self.
    # @param self : P4 object
    # @param ast_obj : AST Object from parser
    # @return None
    def add_AST_obj(self, ast_obj):

        # print "p4 adding AST obj", ast_obj

        try:
            obj_typ = ast_obj.typ
        except AttributeError, err:
            print_syntax_err("Unknown P4 object: '%s'" % str(ast_obj))
            

        if obj_typ == 'header_declaration':
            if ast_obj.name in self.header_decls:
                print_syntax_err('Header decl "%s" already defined.' % ast_obj.name,
                                 ast_obj.string, ast_obj.loc)

            self.header_decls[ast_obj.name] = ast_obj


        elif ( obj_typ == 'header_instance') or ( obj_typ == 'header_stack'):
            if ast_obj.hdr_inst_name in self.header_insts:
                print_syntax_err('Header inst "%s" already defined.' % ast_obj.hdr_inst_name,
                                 ast_obj.string, ast_obj.loc)

            self.header_insts[ast_obj.hdr_inst_name] = ast_obj # inst or stack


        elif ( obj_typ == 'parser_function'):
            if ast_obj.name in self.parser_functions:
                print_syntax_err('Parse function "%s" already defined.' % ast_obj.name,
                                 ast_obj.string, ast_obj.loc)

            self.parser_functions[ast_obj.name] = ast_obj 

        else:
            print "Internal Error: P4:add_AST_obj  Unknown AST_obj", ast_obj.typ
            sys.exit(1)

    ## Finds the named header_decl object and returns it else None
    # @param self : P4 object
    # @param decl_name : name of the hdr_decl object we are looking for
    # @return header_Decl object or None
    def get_header_decl(self, decl_name):
        return self.header_decls.get(decl_name)


    ## Finds the named parser function and return the corresponding parser_function object or None
    # @param self : P4 object
    # @param func_name : name of the parser function (initial state)
    # @return parser_function object or None
    def get_parse_function(self, func_name):
        return self.parser_functions.get(func_name)


    ## Returns the actual named header instance (or stack) or None.
    # @param self : P4 object
    # @param hdr_name : name of the hdr instance
    # @param index    : either '' if hdr is scalar or, if stack, stack index number or 'next'
    # @returns header_inst or header_stack object (or None)
    def get_or_create_hdr_inst(self, hdr_name, index):
        """ This will create a new stack entry if it does not already exist """
        #print "get_hdr_inst:", hdr_name, index
        if index == '':
            return self.header_insts.get(hdr_name)  # scalar
        else:
            # stack
            stack = self.header_insts.get(hdr_name)
            if not stack: 
                raise GP4_Exceptions.RuntimeError, \
                         [ 'Error: stack %s not found.' % hdr_name ]
            if stack.typ != 'header_stack':
                raise GP4_Exceptions.RuntimeError, \
                         ['Error: Header inst "%s" is not a stack.' % hdr_name ]
            h_inst = stack.get_or_create_indexed_instance(index)
            if not h_inst:
                raise GP4_Exceptions.RuntimeError,"stack error: " + hdr_name
            return h_inst


    ## Returns bool indicating if stack index is OK
    # @param self : P4 object
    # @param hdr_name : name of the hdr instance
    # @param index    : stack index number or 'next'
    # @returns Bool
    def check_stack_index(self, hdr_name, index):
        stack = self.header_insts.get(hdr_name)
        if not stack: 
                raise GP4_Exceptions.RuntimeError, \
                         'Error: stack %s not found.' % hdr_name
        if stack.typ != 'header_stack':
                raise GP4_Exceptions.RuntimeError, \
                         'Error: Header inst "%s" is not a stack.' % hdr_name
        return stack.is_legal_index(index)

    ## Returns bool as to whether the hdr inst was declared in source.
    # @param self : P4 object
    # @param hdr_name : name of the hdr instance
    # @returns True if hdr was declared
    def hdr_inst_defined(self, hdr_name):
        return hdr_name in self.header_insts


    ## Prepare the p4 object to parse a new packet.
    # @param self : P4 object
    # @returns None
    def initialize_packet_parser(self):
        self.hdr_extraction_order = [] 



    ## Extracts the fields for the specified header from the given Bits object
    # @param self : P4 object
    # @param hdr  : hdr instance
    # @param bits : Bits object
    # @returns (err, bytes_used, state). return state is just ''
    def extract(self, hdr, bits):
        print "extract bits to hdr",hdr.hdr_inst_name
        err = ''
        bits_used  = 0

        if not hdr.is_valid: 
            err = hdr.create_fields(self)
            if err: return(err, bits_used/8, '')

        for f in hdr.fields:
            num_bits        = int(f.bit_width)
            assert num_bits > 0,"fixme: variable bit width not implemented"
            err, field_bits = bits.get_next_bits(num_bits)
            if err: return(err, bits_used/8, '')
            f.set_value(field_bits, num_bits)
            bits_used += num_bits

        hdr.is_valid = True

        print "extracted",bits_used/8,"bits"
        print hdr
        self.hdr_extraction_order.append(hdr)

        return (err, bits_used/8, '')






    ## Create printable string for Global object
    # @param self : Global object
    # @return String 
    def __str__(self):
        s = 'P4 object'
        s+= 'Hdr decls:'
        s+= ', '.join(self.header_decls.keys())
        s+= '\n'
        return s
