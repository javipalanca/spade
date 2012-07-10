from logic import KB
from pyxf import flora2

class Flora2KB( KB ):
  '''Flora2 knowledge base'''
  def __init__( self, sentence=None, path='runflora' ):
    '''Constructor method
    Usage: Flora2KB( sentence, path )
    sentence - F-logic sentence to be added to the KB (default: None)
    path - path to Flora2 executable (default: 'runflora')'''
    self.flora2 = flora2( path )
    if sentence:
      self.tell( sentence )

  def tell( self, sentence, type='insert' ):
    '''Adds sentence to KB
    Usage: instance.tell( sentence, type )
    sentence - frame logic sentence to be added to KB
    type - insertion type (one of insert, insertall, t_insert, t_insertall, insertrule, newmodule; default: 'insert')'''
    sentence = sentence.strip()
    if sentence[ -1 ] == '.':
      sentence = sentence[ :-1 ]
    return self.flora2.query( type + '{' + sentence + '}' )

  def ask( self, query ):
    '''Queries the KB'''
    return self.flora2.query( query )

  def retract( self, sentence, type='delete' ):
    '''Deletes sentence from KB
    Usage: instance.retract( sentence, type )
    sentence - frame logic sentence to be deleted from KB
    type - deletion type (one of delete, deleteall, erase, eraseall, t_delete, t_deleteall, t_erase, t_eraseall, deletetrule, erasemodule; default: 'delete')'''
    sentence = sentence.strip()
    if sentence[ -1 ] == '.':
      sentence = sentence[ :-1 ]
    return self.flora2.query( type + '{' + sentence + '}' )

  def loadModule( self, module ):
    '''Loads module to KB
    Usage: instance.loadModule( path )
    path - path to module'''
    self.flora2.load( module )

if __name__ == '__main__':
  kb = Flora2KB()
  kb.tell( 'a[ b->c ]' )
  kb.tell( '( ?x[ c->?y ] :- ?x[ b->?y ] )', 'insertrule' )
  for result in kb.ask( '?x[ ?y->?z ]' ):
    print result
  kb.retract( 'a[ b->c ]' )
    

      
