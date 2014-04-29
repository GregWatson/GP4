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
        self.latest = None  # latest extracted header in a parser function.


    


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
                         'Error: stack %s not found.' % hdr_name 
            if stack.typ != 'header_stack':
                raise GP4_Exceptions.RuntimeError, \
                         'Error: Header inst "%s" is not a stack.' % hdr_name
            h_inst = stack.get_or_create_indexed_instance(index)
            if not h_inst:
                raise GP4_Exceptions.RuntimeError, "stack error: " + hdr_name
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

    
    ## Returns bool indicating if field ref is legal (is a defined field)
    # @param self : P4 object
    # @param field_ref : PyParsing field_ref object
    # @returns Bool
    def is_legal_field_ref(self, field_ref):
        assert len(field_ref)==2 # hdr ref, field name
        hdr_ref    = field_ref[0]  # list
        field_name = field_ref[1]  # string

        hdr_inst_name = hdr_ref[0]  # [0] = name, [1]=index if present
    
        if not self.hdr_inst_defined(hdr_inst_name): return False

        # get the hdr decl for this hdr_inst
        hdr_decl_name = self.header_insts[hdr_inst_name].get_decl_name()
        hdr_decl      = self.get_header_decl(hdr_decl_name)

        assert hdr_decl != None

        return hdr_decl.is_legal_field(field_name)


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
    def extract_hdr(self, hdr, bits):
        print "extract bits to hdr",hdr.hdr_inst_name
        err = ''
        bits_used  = 0

        if not hdr.fields_created: 
            err = hdr.create_fields(self)
            if err: return(err, bits_used/8, '')

        for f in hdr.fields:
            num_bits        = int(f.bit_width)
            assert num_bits > 0,"fixme: variable bit width not implemented"
            err, field_bits = bits.get_next_bits(num_bits)
            if err: return(err, bits_used/8, '')
            f.set_value(field_bits, num_bits)
            bits_used += num_bits


        print "extracted",bits_used,"bits."
        print hdr
        self.hdr_extraction_order.append(hdr)
        self.latest = hdr

        return (err, bits_used/8, '')

    ## Set the specified field in given hdr object to given value
    # @param self : P4 object
    # @param hdr  : hdr instance
    # @param field_name : String
    # @param val  : Integer
    # @returns (err, bytes_used, state). return state is just ''
    def set_hdr_field(self, hdr, field_name, val):

        if not hdr.fields_created: 
            err = hdr.create_fields(self)
            if err: return(err, 0, '')

        hdr.set_field(field_name, val)
        return('', 0, '')


    ## Set the specified field in given hdr object to given value
    # @param self : P4 object
    # @param sw_field_ref : List of strings for switc_field_ref
    # @param bits : Bits object
    # @returns (field_value, field_width) both Integers
    def get_sw_field_ref_value_and_width(self, sw_field_ref, bits):
        """ switch field ref can be such as:
            - normal field ref: ['L3_hdr', '2', 'jjj']
            - latest: ['latest.', 'field_s']
            - raw bits: ['current', '4', '6']
        """
        assert len(sw_field_ref)

        if sw_field_ref[0] == 'current': # raw bits, bit_offset, bit_width
            assert len(sw_field_ref) == 3
            bit_offset, bit_width = (int(sw_field_ref[1]), int(sw_field_ref[2]))
            field_value = bits.get_bit_field(bit_offset, bit_width)

        elif  sw_field_ref[0] == 'latest.': # latest.<field_name>
            assert len(sw_field_ref) == 2
            field_name = sw_field_ref[1]
            if not self.latest:
                raise RuntimeError,"'latest' header has not been extracted: latest.%s" % field_name
            # check field name is valid for 'latest'
            if not self.latest.field_has_value(field_name):
                raise RuntimeError,"Field 'latest.%s' has no value (was not extracted?)" % field_name
            field_value = self.latest.get_field(field_name)
            bit_width   = self.latest.get_field_width(field_name)

        else:
            # Normal field ref
            hdr_name  = sw_field_ref[0]
            if len(sw_field_ref) > 2:   # index supplied
                hdr_index  = sw_field_ref[1]
                field_name = sw_field_ref[2]
            else:
                hdr_index  = ''
                field_name = sw_field_ref[1]
            hdr_i = self.get_or_create_hdr_inst(hdr_name, hdr_index)
            if not hdr_i: 
                raise RuntimeError,"Unknown Header '%s' used in switch return." % hdr_name
            if not hdr_i.field_has_value(field_name):
                raise RuntimeError,"Field '%s.%s' is not valid." % (hdr_name, field_name)

            field_value = hdr_i.get_field(field_name)
            bit_width   = hdr_i.get_field_width(field_name)

        print "get_sw_field_ref_value_and_width(", sw_field_ref,") got",bit_width,"bits: 0x%x" % field_value
        return(field_value, bit_width)




    ## Create printable string for Global object
    # @param self : Global object
    # @return String 
    def __str__(self):
        s = 'P4 object'
        s+= 'Hdr decls:'
        s+= ', '.join(self.header_decls.keys())
        s+= '\n'
        return s
