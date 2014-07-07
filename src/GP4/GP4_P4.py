# P4  object - contains structures compiled from a P4 program
#
## @package GP4

from GP4_Utilities import *
import GP4_Exceptions
import GP4_Action
import sys

class P4(object):

    ## Constructor for P4 object
    # @param self : New P4 object
    # @return self
    def __init__(self):

        self.header_decls = {} # maps name of header_decl to header_decl object
        self.header_insts = {} # maps inst name of header_inst to header_inst or header_stack object
        self.parser_functions = {}  # maps parser function name (string) to parse function object
        self.control_functions = {} # maps control function name (string) to control function object
        self.tables  = {}  # maps table name to table object
        self.actions = {}  # maps action name to action object
        self.deparsers = {} # maps deparser name to deparser object

        # run time fields per processed packet 
        self.hdr_extraction_order = []  # list of header objects in the order they were extracted.
        self.latest = None  # latest extracted header in a parser function.
        self.modified_fields = []  # list of fields or headers that are modified by actions.


    ## Check self-consistency where possible. More checking is done at run-time.
    # @param self : P4 object
    # @return None. Raises runtime error if there is a problem.
    def check_self_consistent(self):
        for tbl_name in self.tables:
            tbl = self.get_table(tbl_name)
            if tbl:
                tbl.check_self_consistent(self)
            else:
                raise GP4_Exceptions.RuntimeError, 'Table "%s" undefined' % tbl_name

        for action_name in self.actions:
            action = self.get_action_by_name(action_name)
            if action:
                action.check_self_consistent(self)
            else:
                raise GP4_Exceptions.RuntimeError, 'Action "%s" undefined' % action_name


    ## Add a new object (e.g. header_decl) to self.
    # @param self : P4 object
    # @param ast_obj : AST Object from parser
    # @return None
    def add_AST_obj(self, ast_obj):

        try:
            obj_typ = ast_obj.typ
        except AttributeError, err:
            print_syntax_err("Unknown P4 object: '%s'" % str(ast_obj))

        # print "p4 adding AST obj", ast_obj,"of type", ast_obj.typ

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

        elif ( obj_typ == 'control_function'):
            if ast_obj.name in self.control_functions:
                print_syntax_err('Control function "%s" already defined.' % ast_obj.name,
                                 ast_obj.string, ast_obj.loc)

            self.control_functions[ast_obj.name] = ast_obj 

        elif ( obj_typ == 'table'):
            if ast_obj.name in self.tables:
                print_syntax_err('Table "%s" already defined.' % ast_obj.name,
                                 ast_obj.string, ast_obj.loc)

            self.tables[ast_obj.name] = ast_obj 

        elif ( obj_typ == 'action'):
            if ast_obj.name in self.actions:
                print_syntax_err('Action "%s" already defined.' % ast_obj.name,
                                 ast_obj.string, ast_obj.loc)

            self.actions[ast_obj.name] = ast_obj 

        elif ( obj_typ == 'deparser'):
            if ast_obj.name in self.deparsers:
                print_syntax_err('Deparser "%s" already defined.' % ast_obj.name,
                                 ast_obj.string, ast_obj.loc)

            self.deparsers[ast_obj.name] = ast_obj 

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


    ## Finds the named control function and returns the corresponding function object or None
    # @param self : P4 object
    # @param func_name : name of the control function
    # @return ctrl_function object or None
    def get_control_function(self, func_name):
        return self.control_functions.get(func_name)


    ## Finds the named table and returns the corresponding table object or None
    # @param self : P4 object
    # @param table_name : name of the table
    # @return table object or None
    def get_table(self, table_name):
        return self.tables.get(table_name)


    ## Finds the named action and returns the corresponding action object or None
    # @param self : P4 object
    # @param action_name : name of the action
    # @return action object or None
    def get_action_by_name(self, action_name):
        return self.actions.get(action_name)



    ## Finds the named deparser and returns the corresponding object or None
    # @param self : P4 object
    # @param deparser_name : name of the deparser
    # @return deparser object or None
    def get_deparser_by_name(self, deparser_name):
        return self.deparsers.get(deparser_name)


    ## Finds the named action and then executes it with the given arguments.
    # @param self : P4 object
    # @param action_name : name of the action
    # @param args : args list
    # @return None
    def execute_action_by_name(self, action_name, *args):
        action = self.actions.get(action_name)
        if not action:
            raise GP4_Exceptions.RuntimeError, \
                "Called action %s but that action is not defined." % action_name
        action.execute(self, *args)



    ## Returns the actual named header instance (or stack) or None.
    # @param self : P4 object\
    # @param hdr_name : name of the hdr instance
    # @param hdr_index    : either '' if hdr is scalar or, if stack, stack index number or 'next'
    # @returns header_inst or header_stack object (or None)
    def get_or_create_hdr_inst(self, hdr_name, hdr_index):
        """ This will create a new stack entry if it does not already exist """
        #print "get_or_create_hdr_inst:", hdr_name, hdr_index
        if hdr_index == '':
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
            h_inst = stack.get_or_create_indexed_instance(hdr_index)
            if not h_inst:
                raise GP4_Exceptions.RuntimeError, "stack error: " + hdr_name
            return h_inst



    ## Returns hdr object if created, else raise Runtime error
    # @param self : P4 object
    # @param hdr_name : name of the hdr instance
    # @param hdr_index    : either '' if hdr is scalar or, if stack, stack index number
    # @returns Header_Instance object or None or raises RunTime error
    def get_hdr_inst(self, hdr_name, hdr_index, raiseError=True):
        """ runtime error if hdr doesnt even exist """
        #print "get_hdr_inst:", hdr_name, hdr_index
        if hdr_index == '':
            hdr = self.header_insts.get(hdr_name)  # scalar
            if not hdr:
                if raiseError:
                    raise GP4_Exceptions.RuntimeError, \
                             'Error: hdr %s not found.' % hdr_name 
                else: return None
            return hdr
        else:
            # stack
            stack = self.header_insts.get(hdr_name)

            if not stack: 
                if raiseError:
                    raise GP4_Exceptions.RuntimeError, \
                             'Error: hdr stack %s not found.' % hdr_name 
                else: return None

            if stack.typ != 'header_stack':
                if raiseError:
                    raise GP4_Exceptions.RuntimeError, \
                             'Error: hdr %s not defined or else not a stack.' % hdr_name 
                else: return None
            h_inst = stack.get_indexed_instance(hdr_index)

            if not h_inst:
                if raiseError:
                    raise GP4_Exceptions.RuntimeError, \
                             'Error: hdr %s not defined.' % hdr_name 
                else: return None

            return h_inst



    ## Returns bool indicating if hdr inst's fields are created
    # @param self : P4 object
    # @param hdr_name : name of the hdr instance
    # @param hdr_index    : either '' if hdr is scalar or, if stack, stack index number
    # @returns Boolean
    def check_hdr_inst_is_valid(self, hdr_name, hdr_index):
        """ runtime error if hdr doesnt even exist """
        #print "check_hdr_inst_is_valid:", hdr_name, hdr_index
        if not self.hdr_inst_defined( hdr_name ):
            raise GP4_Exceptions.RuntimeError, \
                'Header "%s" not defined.' % hdr_name
        else:
            try:
                hdr = self.get_hdr_inst( hdr_name, hdr_index)
            except GP4_Exceptions.RuntimeError :
                return False
        return hdr.fields_created



    ## Returns bool indicating if stack index is OK
    # @param self : P4 object
    # @param hdr_name : name of the hdr instance
    # @param hdr_index    : stack index number or 'next'
    # @returns Bool
    def check_stack_index(self, hdr_name, hdr_index):
        stack = self.header_insts.get(hdr_name)
        if not stack: 
                raise GP4_Exceptions.RuntimeError, \
                         'Error: stack %s not found.' % hdr_name
        if stack.typ != 'header_stack':
                raise GP4_Exceptions.RuntimeError, \
                         'Error: Header inst "%s" is not a stack.' % hdr_name
        return stack.is_legal_index(hdr_index)

    
    ## Returns bool indicating if field ref is legal (is a defined field)
    # @param self : P4 object
    # @param field_ref : PyParsing field_ref object
    # @returns Bool
    def is_legal_field_ref(self, field_ref):
        if not len(field_ref)==2: return False
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
        self.latest = None
        for hdr in self.header_insts.keys(): self.header_insts[hdr].initialize()
        self.modified_fields = []

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
            num_bits = get_integer(f.bit_width)

            if num_bits == 0 : # Need to compute length expression for header.
                num_bits = hdr.compute_remaining_header_length_bits(self)

            err, field_bits = bits.get_next_bits(num_bits)
            if err: return(err, bits_used/8, '')
            f.set_value(field_bits, num_bits)
            bits_used += num_bits


        print "extracted",bits_used,"bits."
        print hdr
        self.hdr_extraction_order.append(hdr)
        self.latest = hdr

        return (err, bits_used/8, '')



    ## Deparse the current packet
    # @param self : P4 object
    # @param pkt  : [ byte ]   Ingress pkt.
    # @param bytes_used : Integer    num bytes of pkt used in parsing.
    # @returns pkt_out : [ byte ]
    def deparse_packet(self, pkt, bytes_used):
        print "deparsing..."
        pkt_out = []

        if not len(self.deparsers):   # default is to put headers back in order they were parsed
            for hdr in self.hdr_extraction_order:
                pkt_out.extend(hdr.serialize_fields())

        else:
            assert len(self.deparsers)==1,"Sorry, can only have one deparser at the moment!"
            dprsr_names = self.deparsers.keys()
            dprsr_name  = dprsr_names[0]
            dprsr       = self.get_deparser_by_name(dprsr_name)
            print "Deparsing packet using: ",dprsr
            for hdr_or_field_ref in dprsr.refs:
                hdr_or_field = self.get_hdr_or_field_from_ref(hdr_or_field_ref)
                if not hdr_or_field or not hdr_or_field.fields_created:
                    continue  # skip any invalid headers
                pkt_out.extend(hdr_or_field.serialize_fields())

        pkt_out.extend(pkt[bytes_used:])
        return pkt_out




    ## Set the specified field in given hdr object to given value (immediate assign to value)
    # @param self : P4 object
    # @param hdr  : hdr instance
    # @param field_name : String
    # @param val  : Integer
    # @returns (err, bytes_used, state). return state is just ''
    def set_hdr_field(self, hdr, field_name, val):
        """ This is a blocking assign. Dont use in actions which need non-blocking assign.
        """

        if not hdr.fields_created: 
            err = hdr.create_fields(self)
            if err: return(err, 0, '')

        hdr.set_field(field_name, val)
        return('', 0, '')


    ## Get (value,width) from field refs expressed as strings from a switch_field_ref stmt
    # @param self : P4 object
    # @param sw_field_ref : List of strings for switch_field_ref
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
            bit_offset, bit_width = (get_integer(sw_field_ref[1]), get_integer(sw_field_ref[2]))
            field_value = bits.get_bit_field(bit_offset, bit_width)

        elif  sw_field_ref[0] == 'latest.': # latest.<field_name>
            assert len(sw_field_ref) == 2
            field_name = sw_field_ref[1]
            if not self.latest:
                raise RuntimeError,"'latest' header has not been extracted: latest.%s" % field_name
            # check field name is valid for 'latest'
            if not self.latest.field_has_value(field_name):
                raise RuntimeError,"Field 'latest.%s' has no value (was not extracted?)" % field_name
            field_value = self.latest.get_field_value(field_name)
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

            field_value = hdr_i.get_field_value(field_name)
            bit_width   = hdr_i.get_field_width(field_name)

        print "get_sw_field_ref_value_and_width(", sw_field_ref,") got",bit_width,"bits: 0x%x" % field_value
        return(field_value, bit_width)


    ## Get field object given hdr, hdr_index and field name
    # @param self : P4 object
    # @param hdr_name   : String
    # @param hdr_index  : String
    # @param field_name : String
    # @returns field object else None
    def get_field(self, hdr_name, hdr_index, field_name):
        hdr_i = self.get_hdr_inst(hdr_name, hdr_index, raiseError=False)
        if hdr_i: return hdr_i.get_field(field_name)
        else: return None


    ## Get either field object or header object from ref object (field_ref or hdr_ref)
    # @param self : P4 object
    # @param ref  : PyParse field_ref or hdr_ref
    # @returns object else None
    def get_hdr_or_field_from_ref(self, ref):

        if is_field_ref(ref): return  self.get_field_from_field_ref(ref)
        else: return  self.get_header_from_header_ref(ref)

 

    ## Get field object from field_ref object
    # @param self    : P4 object
    # @param field_ref : PyParse field_ref list
    # @returns field object else None
    def get_field_from_field_ref(self, field_ref):

        hdr_name, hdr_index ,field_name = get_hdr_hdr_index_field_name_from_field_ref(field_ref)
        return self.get_field(hdr_name, hdr_index ,field_name)


    ## Get header instance object from field_ref object
    # @param self    : P4 object
    # @param field_ref : PyParse field_ref list
    # @returns header Instance object else None
    def get_header_from_field_ref(self, field_ref):
        hdr_name, hdr_index ,field_name = get_hdr_hdr_index_field_name_from_field_ref(field_ref)
        hdr_i = self.get_hdr_inst(hdr_name, hdr_index, raiseError=False)
        if hdr_i: return hdr_i
        else: return None


    ## Get header instance object from hdr_ref object
    # @param self    : P4 object
    # @param hdr_ref : PyParse hdr_ref list
    # @returns header Instance object else None
    def get_header_from_header_ref(self, hdr_ref):
        hdr_name, hdr_index = get_hdr_hdr_index_from_hdr_ref(hdr_ref)
        hdr_i = self.get_hdr_inst(hdr_name, hdr_index, raiseError=False)
        if hdr_i: return hdr_i
        else: return None




    ## Add the given field or hdr to the list that have been changed via non-blocking assigns.
    # @param self    : P4 object
    # @param field   : field object
    # @returns None
    def add_modified_field(self, field):
        self.modified_fields.append(field)


    ## Update all the actual header fields that were modified by the last table action.
    # @param self    : P4 object
    # @returns None
    def update_modified_fields(self):
        print "update_modified_fields:", self.modified_fields
        for f in self.modified_fields:
            f.update_value()

        self.modified_fields = []





    ## Set up the standard built-in actions
    # @param self : P4 object
    # @returns None
    def load_default_actions(self):
        self.actions['no_action'] = \
             GP4_Action.Action('', 0, 'no_action',GP4_Action.no_action, num_args=0 )
        self.actions['add_to_field'] = \
            GP4_Action.Action('', 0, 'add_to_field', GP4_Action.add_to_field, num_args=2)
        self.actions['modify_field'] = \
            GP4_Action.Action('', 0, 'modify_field', GP4_Action.modify_field, num_args=2)
        self.actions['add_header'] = \
            GP4_Action.Action('', 0, 'add_header', GP4_Action.add_header, num_args=1)
        self.actions['copy_header'] = \
            GP4_Action.Action('', 0, 'copy_header', GP4_Action.copy_header, num_args=2)
        

    ## Create printable string for Global object
    # @param self : Global object
    # @return String 
    def __str__(self):
        s = 'P4 object'
        s+= 'Hdr decls:'
        s+= ', '.join(self.header_decls.keys())
        s+= '\n'
        s+= 'Hdr insts:'
        s+= ', '.join(self.header_insts.keys())
        s+= '\n'
        return s
