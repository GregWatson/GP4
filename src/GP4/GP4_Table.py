# GP4_Table.py : P4 Table Object
#
## @package GP4
#
# This is a table Instance (all Tables are unique)

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
    # @param action_next_table : List of Pyparsing action_next_table objects
    # @param min_size : Integer. 
    # @param max_size : Integer. 
    # @returns self
    def __init__(self, string, loc, name, field_matches=[], actions={}, 
                                          min_size=1, max_size=256 ):
        
        super(Table, self).__init__(string, loc, 'table')

        self.name              = name
        self.field_matches     = field_matches
        self.action_next_table = actions # dict maps action name to next_table name 
                                         #     (or '' if no next_table)
        self.min_size          = min_size
        self.max_size          = max_size
        self.size              = 0      # Actual size. Not same as number of entries.
        self.entries           = []     # List of Entry objects
        self.num_entries       = 0      # Actual number of entries installed.
        self.match_key_fun     = None   # function to construct match key List for this Table
        self.default_action    = [ 'no_action' ] # [ action_name, [params*] ] Used if no match. Set at run time.
        

    ## Set default action
    # @param self : table object
    # @param action : Pyparsing param list
    # @return Bool: Success or Fail
    def set_default_action(self, *action):
        print "Table:",self.name,"setting default action to:", action[0]
        self.default_action = action[0]
        return True
       

    ## Check self-consistency where possible. More checking is done at run-time.
    # @param self : table object
    # @param p4   : p4 object
    # @return None. Raises runtime error if there is a problem.
    def check_self_consistent(self, p4):

        for action in self.action_next_table:

            if not p4.get_action_by_name(action):
                raise GP4_Exceptions.RuntimeError, 'Table "%s" specifies undefined action "%s"' % \
                    (self.name, action)

            nxt_table = self.action_next_table[action]  # '' if no next table

            if nxt_table != '':
                if nxt_table == self.name:  # recursion!
                    raise GP4_Exceptions.RuntimeError, \
                        'Table "%s" action "%s" specifies self as next_table: recursion is not allowed.' % \
                        (self.name, action)

                if not p4.get_table(nxt_table):
                    raise GP4_Exceptions.RuntimeError, \
                        'Table "%s" action "%s" specifies undefined next_table "%s"' % \
                        (self.name, action, nxt_table)




    ## Apply this table with a P4 argument as context.
    # @param self : table object
    # @param p4   : p4 object
    # @returns None
    def apply( self, p4 ):
        print "Applying table", str(self)

        idx = -1
        if self.num_entries:
            match_keys = self.create_match_keys(p4)
            if match_keys:
                for mk in match_keys: print "match_key=",str(mk)

            # get table entry index of first match
            idx = self.lookup_match_keys(match_keys)
            if idx != -1: 
                print "Table",self.name,"matched on idx",idx
                action_args = self.entries[idx].get_action()
                #print "action args:", action_args


        if idx == -1: # no match
            # choose default action
            action_args = self.default_action
            #print "No matches. using default action",action_args
            if not action_args:
                raise GP4_Exceptions.RuntimeError, "Table '%s' has no default action." % self.name
        
        action_name = action_args[0]
        action = p4.get_action_by_name(action_name)
        if not action:
            raise GP4_Exceptions.RuntimeError, "Unknown action '%s'" % action_name

        action.execute(p4, *action_args[1:] )
        
        # If we have a next_table defined for this action then we need to execute it.
        next_table_name = self.action_next_table.get(action_name)
        if next_table_name :
            tbl = p4.get_table(next_table_name)
            if not tbl:
                raise GP4_Exceptions.RuntimeError, "Unknown Table '%s'" % next_table_name
            tbl.apply(p4)


    ## Construct the match key from current header instances.
    # @param self : table object
    # @param p4   : p4 object
    # @returns list of Match_Key objects
    def create_match_keys( self, p4 ):
        if not self.match_key_fun:
            self.match_key_fun = self.compile_match_key_fun(p4)
        return self.match_key_fun(p4)


       
    ## Compile the self.match_key_fun function
    # @param self : table object
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



    ## Find an entry that matches the match_keys list. Return index or -1 if no match
    # @param self : table object
    # @param match_keys : [ Match_Key ]
    # @returns Integer: index in self.entries or -1 if no match
    def lookup_match_keys(self, match_keys):
        print "lookup_match_keys(", 
        for mk in match_keys: print mk,
        print ")"

        #fixme - needs to much more efficient
        for (ix,entry) in enumerate(self.entries):
            if entry.matches(match_keys):
                return ix
        return -1




    ## Check action statement is legal for this table
    # @param self : table object
    # @param action_stmt : pyparse action_stmt
    # @returns Bool: success or Failure
    def check_action(self, action_stmt):
        print "check_action:", action_stmt
        return action_stmt[0] in self.action_next_table.keys()



    ## Runtime command to add an entry to a table
    # @param self : table object
    # @param pos  : position in table. None = anywhere.
    # @param args : Tuple ( entry_list, action_stmt )
    # @returns Bool: success or Failure
    def add_entry( self, pos, *args ):
        print "add_entry: pos=",pos,"args=",args
        assert len(args)==2

        entry_list = args[0]  # [ num | (num,num) ]
        action_stmt = args[1]

        #fixme - check entry not already in table.
        
        # create a new Entry with EntryVals=entry_list and action=action_stmt
        entry = Entry()
        entry.set_matchList(entry.make_match_vals_from_pyparse(entry_list))

        if not self.check_action(action_stmt):
            raise GP4_Exceptions.RuntimeError, "Table '%s' cannot do action %s." % (self.name, action_stmt)
        entry.set_action(action_stmt)
        if pos == 'any':
            if self.num_entries >= self.max_size:
                print "Table",self,"full"
                return False  # full - cant add more.
            self.entries.append(entry)
            self.num_entries += 1
        else:
            assert False,"Sorry. table.add_entry to specific location not inmplemented."

        print "add_entry done: Table",self
        return True        



    def __str__(self):
        s = self.name + '() [min=%d max=%d num=%d]\n' % (self.min_size, self.max_size, self.num_entries)
        if len(self.field_matches):
            s+='   Field matches:'
            for el in self.field_matches:
                s += str(el) + ';'
            s+='\n'
        if len(self.action_next_table):
            s+='   Actions:\n'
            for el in self.action_next_table:
                s += "      Action '%s' => next table '%s';\n" % (el, self.action_next_table[el])
            s+='\n'

        return s
