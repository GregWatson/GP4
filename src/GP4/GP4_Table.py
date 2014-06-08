# GP4_Table.py : P4 Table Object
#
## @package GP4

from GP4_Utilities  import *
#from GP4_Parser_Function_Code import *
from GP4_AST_object import AST_object
import GP4_Exceptions
import sys

class Table(AST_object):

    ## Construct new Table object.
    # @param self : object
    # @param string : String.  Source text
    # @param loc    : Integer. location in text of this object
    # @param name   : String. Name of the Table
    # @param field_matches : List of Pyparsing field_match objects
    # @param actions  : List of Pyparsing action_next_table objects
    # @param min_size : Integer. 
    # @param max_size : Integer. 
    # @returns self
    def __init__(self, string, loc, name, field_matches=[], actions=[], 
                                          min_size=None, max_size=None ):
        
        super(Table, self).__init__(string, loc, 'table')

        self.name           = name
        self.field_matches  = field_matches
        self.actions        = actions
        self.min_size       = min_size
        self.max_size       = max_size
        self.size           = 0      # Actual size. Not same as number of entries.
        self.num_entries    = 0      # Actual number of entries installed.
        self.match_key_fun  = None   # function to construct match key List for this Table
        self.default_action = None   # in case of no matches. set at run time.

    ## Apply this table with a P4 argument as context.
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @returns None
    def apply( self, p4 ):
        print "Applying table", str(self)

        #if self.size:
        match_keys = self.create_match_keys(p4)
        #else:
        #    actions = self.default_action
        if match_keys:
            for mk in match_keys: print "match_key=",str(mk)


    ## Construct the match key from current header instances.
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @returns list of Match_Key objects
    def create_match_keys( self, p4 ):
        if not self.match_key_fun:
            self.match_key_fun = self.compile_match_key_fun(p4)
        return self.match_key_fun(p4)


       
    ## Compile the self.match_key_fun function
    # @param self : Control_Function object
    # @param p4   : p4 object
    # @returns function f(p4): return  [ Match_Key ]
    def compile_match_key_fun( self, p4 ):
        """ The match_key_fun should return a list of Match_Keys based on the
            current header fields. An undefined field returns a Match_Key with
            a length of zero. i.e.:
            match_key_fun(p4) : return [ Match_Key ]
        """
        print "compile_match_key_fun"

        # If nothing specified in the "reads" expression then return None
        if not len( self.field_matches ):
            return lambda p4: None

        codeL = [ 'def f(p4):', '   match_keyL = []' ]
        for fm in self.field_matches: 
            print '   ',fm
            assert len(fm)==2 # 0=[hdr,field,mask]  1=type
            mask = 0 if len(fm[0])==1 else fm[0][1]
            field_ref = fm[0][0]

            hdr_name, hdr_index, field_name = get_hdr_hdr_index_field_name_from_field_ref(field_ref)
            print "hdr:",hdr_name,"hdr_index:",hdr_index,"field:",field_name,"mask:",mask

            codeL.append( '   field = p4.get_field("%s","%s","%s")' % ( hdr_name, hdr_index, field_name ))
            codeL.append( '   match_key = field.make_Match_Key() if field else Match_Key()' )
            if mask:
                codeL.append( '   if match_key.valid : match_key.value &= %s' % mask)
            codeL.append( '   match_keyL.append(match_key)')

        codeL.append('   return match_keyL' )
        
        for l in codeL: print l

        code = '\n'.join(codeL)

        try: 
            exec code in globals(), locals()
        except Exception as ex_err:
            print "Error: generated code for python function yielded exception:",ex_err.data
            print "code was <\n",code,"\n>\n"
            raise GP4_Exceptions.RuntimeError, ex_err.data

        return f



    def __str__(self):
        s = self.name + '()\n'
        if len(self.field_matches):
            s+='   Field matches:'
            for el in self.field_matches:
                s += str(el) + ';'
            s+='\n'
        if len(self.actions):
            s+='   Actions:'
            for el in self.actions:
                s += str(el) + ';'
            s+='\n'

        return s
