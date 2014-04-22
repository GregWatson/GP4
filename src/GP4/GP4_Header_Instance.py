# GP4_Header_Instance.py Header Instance Object
#
## @package GP4

from GP4_Utilities  import print_syntax_err
from GP4_AST_object import AST_object

class Header_Instance(AST_object):

    ## Construct new Header_Instance object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param hdr_type_name   : String. Name of the header decl that this is an instance of.
    # @param hdr_is_metadata : Bool 
    # @param hdr_inst_name   : String. Name of this instance.
    # @returns self
    def __init__(self, string, loc, 
                hdr_type_name, hdr_is_metadata, hdr_inst_name):
        
        super(Header_Instance, self).__init__(string, loc, 'header_instance')

        self.hdr_type_name    = hdr_type_name    # name of hdr decl that this instantiates
        self.hdr_is_metadata  = hdr_is_metadata  # Bool.
        self.hdr_inst_name    = hdr_inst_name    # name of this instance

        self.fields_created = False   # Bool. Set when fields are actually created (extracted)
        self.fields         = []      # ordered list of Field objects
        self.field_names    = []      # ordered list of field names



    ## Instantiate the actual fields from the header_decl
    # @param self : object
    # @returns err String: '' is no error
    def create_fields(self, p4): 

        decl = p4.get_header_decl(self.hdr_type_name)
        if not decl:
            return('Unknown header declaration "%s" referenced by header instance "%s"' %
                    (self.hdr_type_name, self.hdr_inst_name) )

        self.fields         = decl.copy_fields()
        self.field_names    = [ f.name for f in self.fields ]
        self.fields_created = True

        print "Created fields for",self.hdr_inst_name
        return ''




    ## Set field to given value
    # @param self : object
    # @param field_name : String
    # @param val : Integer
    # @return None    
    def set_field(self, field_name, val): 

        for ix,fname in enumerate(self.field_names):
            if fname == field_name:
                self.fields[ix].set_value( val )
                print "set %s.%s to %s" % (self.hdr_inst_name, field_name, val)
                return
                
        assert False,"set_field: Unknown field name %s" % field_name



    ## Get value of field
    # @param self : object
    # @param field_name : String
    # @return val : Integer
    def get_field(self, field_name): 

        for ix,fname in enumerate(self.field_names):
            if fname == field_name:
                return self.fields[ix].get_value()

        return None


    ## Return the name of the declaration for this instance
    # @param self : object
    # @returns String
    def get_decl_name(self):
        return self.hdr_type_name


    def __str__(self):
        s = self.hdr_type_name + ' ' + self.hdr_inst_name
        s += ' [metadata]' if self.hdr_is_metadata else ''
        if self.fields_created:
            s += '\n'
            for f in self.fields: s += '   ' + str(f) + '\n'
        return s
