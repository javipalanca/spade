from logic import KB
from pyxf import xsb

class XSBKB( KB ):
  '''XSB Prolog knowledge base'''
  def __init__( self, sentence=None, path='xsb' ):
    '''Constructor method
    Usage: XSBKB( sentence, path )
    sentence - Prolog sentence to be added to the KB (default: None)
    path - path to XSB executable (default: 'xsb')'''
    self.xsb = xsb( path )
    if sentence:
      self.tell( sentence )

  def tell( self, sentence ):
    '''Adds sentence to KB'''
    sentence = sentence.strip()
    if sentence[ -1 ] == '.':
      sentence = sentence[ :-1 ]
    return self.xsb.query( 'assert(' + sentence + ')' )

  def ask( self, query ):
    '''Queries the KB'''
    return self.xsb.query( query )

  def retract( self, sentence ):
    '''Deletes sentence from KB'''
    sentence = sentence.strip()
    if sentence[ -1 ] == '.':
      sentence = sentence[ :-1 ]
    return self.xsb.query( 'retract(' + sentence + ')' )

  def loadModule( self, module ):
    '''Loads module to KB
    Usage: instance.loadModule( path )
    path - path to module'''
    self.xsb.load( module )
    
if __name__ == '__main__':
  kb = XSBKB()
  kb.tell( 'a(b,c)' )
  kb.tell( 'a(c,d)' )
  kb.tell( '( p(_X,_Y) :- a(_X,_Y) )' )
  kb.tell( '( p(_X,_Y) :- a(_X,_Z), p(_Z,_Y) )' )
  for result in kb.ask( 'p(X,Y)' ):
    print result
  kb.retract( 'a(b,c)' )
      
