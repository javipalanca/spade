__doc__ = ''' Python interface to XSB Prolog, SWI Prolog, ECLiPSe Prolog and Flora2
 by Markus Schatten <markus_dot_schatten_at_foi_dot_hr>
 Faculty of Organization and Informatics,
 Varazdin, Croatia, 2011

 This library is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 2.1 of the License, or (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public
 License along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA'''

__version__ = '1.0.1'

import pexpect as px
import re

xsbprompt = '[|][ ][?][-][ ]'
xsberror = '[+][+]Error.*'

var_re = re.compile( '[^a-zA-Z0-9_]([A-Z][a-zA-Z0-9_]*)' )
res_re = re.compile( "res[\(]'([A-Z][a-zA-Z0-9_]*)',[ ]?(.*)[\)]" )

class XSBExecutableNotFound( Exception ):
  '''Exception raised if XSB executable is not found on the specified path.'''
  pass

class XSBCompileError( Exception ): 
  '''Exception raised if loaded module has compile errors.'''
  pass

class XSBQueryError( Exception ): 
  '''Exception raised if query raises an error.'''
  pass

class xsb:
  '''Python interface to XSB Prolog (http://xsb.sf.net)'''
  def __init__( self, path='xsb', args='--nobanner --quietload' ):
    '''Constructor method
    Usage: xsb( path, args )
    path - path to XSB executable (default: 'xsb')
    args - command line arguments (default: '--nobanner --quietload')

    self.engine becomes pexpect spawn instance of XSB Prolog shell

    Raises: XSBExecutableNotFound'''
    try:
      self.engine = px.spawn( path + ' ' + args, timeout=5 )
      self.engine.expect( xsbprompt )
    except px.ExceptionPexpect:
      raise XSBExecutableNotFound, 'XSB executable not found on the specified path. Try using xsb( "/path/to/XSB/bin/xsb" )'
    
  def load( self, module ):
    '''Loads module into self.engine
    Usage: instance.load( path )
    path - path to module file

    Raises: XSBCompileError'''
    self.engine.sendline( "['" + module + "']." ) 
    index = self.engine.expect( [ xsbprompt, xsberror ] )
    if index == 1:
      raise XSBCompileError, 'Error while compiling module "' + module + '". Error from XSB:\n' + self.engine.after 
    
  def query( self, query ):
    '''Queries current engine state
    Usage: instance.query( query )
    query - usual XSB Prolog query (example: 'likes( X, Y )')

    Returns:
      True - if yes/no query and answer is yes
      False - if yes/no query and answer is no
      List of dictionaries - if normal query. Dictionary keys are returned
      variable names. Example:
      >>> instance.query( 'likes( Person, Food )' )
      [{'Person': 'john', 'Food': 'curry'}, {'Person': 'sandy', 'Food': 'mushrooms'}]

    Raises: XSBQueryError'''
    query = query.strip()
    if query[ -1 ] != '.':
      query += '.'
    lvars = var_re.findall( query )
    lvars = list( set( lvars ) )
    if lvars == []: # yes/no query (no variables)
      self.engine.sendline( query )
      index = self.engine.expect( [ xsbprompt, xsberror ] )
      if index == 1:
	raise XSBQueryError, 'Error while executing query "' + query + '". Error from XSB:\n' + self.engine.after
      else:
	if 'yes' in self.engine.before:
	  return True
	else:
	  return False
    else: # normal query
      printer = self._printer( lvars, query )
      self.engine.sendline( printer )
      index = self.engine.expect( [ xsberror, xsbprompt ] )
      if index == 0:
	raise XSBQueryError, 'Error while executing query "' + query + '". Error from XSB:\n' + self.engine.after
      else:
	res = res_re.findall( self.engine.before.split( ',nl,fail.\n' )[ -1 ] )
	results = []
	counter = 0
	temp = []
	for i in res:
	  counter += 1
	  temp.append( i )
	  if counter % len( lvars ) == 0:
	    results.append( dict( temp ) )
	    temp = []
	if results == []:
	  return False
	return results
	
  def _printer( self, lvars, query ):
    '''Private method for constructing a result printing query.
    Usage: instance._printer( lvars, query )
    lvars - list of logical variables to print
    query - query containing the variables to be printed

    Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
    '''
    query = query[ :-1 ]
    elems = [ "writeln( res('''" + i + "'''," + i + ") )" for i in lvars ]
    printer = query + ',' + ','.join( elems ) + ',nl,fail.'
    return printer

swiprompt = '[?][-][ ]'
swierror = 'ERROR.*'

class SWIExecutableNotFound( Exception ):
  '''Exception raised if SWI-Prolog executable is not found on the specified path.'''
  pass

class SWICompileError( Exception ): 
  '''Exception raised if loaded module has compile errors.'''
  pass

class SWIQueryError( Exception ): 
  '''Exception raised if query raises an error.'''
  pass

class swipl:
  '''Python interface to SWI Prolog (http://www.swi-prolog.org)'''
  def __init__( self, path='swipl', args='-q +tty' ):
    '''Constructor method
    Usage: swipl( path, args )
    path - path to SWI executable (default: 'swipl')
    args - command line arguments (default: '-q +tty')

    self.engine becomes pexpect spawn instance of SWI Prolog shell

    Raises: SWIExecutableNotFound'''
    try:
      self.engine = px.spawn( path + ' ' + args, timeout=5 )
      self.engine.expect( swiprompt )
    except px.ExceptionPexpect:
      raise SWIExecutableNotFound, 'SWI-Prolog executable not found on the specified path. Try installing swi-prolog or using swipl( "/path/to/swipl" )'
    
  def load( self, module ):
    '''Loads module into self.engine
    Usage: instance.load( path )
    path - path to module file

    Raises: SWICompileError'''
    self.engine.sendline( "['" + module + "']." ) 
    index = self.engine.expect( [ swierror, swiprompt ] )
    if index == 0:
      raise SWICompileError, 'Error while compiling module "' + module + '". Error from SWI:\n' + self.engine.after 
    
  def query( self, query ):
    '''Queries current engine state
    Usage: instance.query( query )
    query - usual SWI Prolog query (example: 'likes( X, Y )')

    Returns:
      True - if yes/no query and answer is yes
      False - if yes/no query and answer is no
      List of dictionaries - if normal query. Dictionary keys are returned
      variable names. Example:
      >>> instance.query( 'likes( Person, Food )' )
      [{'Person': 'john', 'Food': 'curry'}, {'Person': 'sandy', 'Food': 'mushrooms'}]

    Raises: SWIQueryError'''
    query = query.strip()
    if query[ -1 ] != '.':
      query += '.'
    lvars = var_re.findall( query )
    lvars = list( set( lvars ) )
    if lvars == []: # yes/no query (no variables)
      self.engine.sendline( query )
      index = self.engine.expect( [ swiprompt, swierror ] )
      if index == 1:
	raise SWIQueryError, 'Error while executing query "' + query + '". Error from SWI:\n' + self.engine.after
      else:
	if 'true' in self.engine.before:
	  return True
	else:
	  return False
    else: # normal query
      printer = self._printer( lvars, query )
      self.engine.sendline( printer )
      index = self.engine.expect( [ swierror, swiprompt ] )
      if index == 0:
	raise SWIQueryError, 'Error while executing query "' + query + '". Error from SWI:\n' + self.engine.after
      else:
	res = res_re.findall( self.engine.before.split( ',nl,fail.\n' )[ -1 ] )
	results = []
	counter = 0
	temp = []
	for i in res:
	  counter += 1
	  temp.append( i )
	  if counter % len( lvars ) == 0:
	    results.append( dict( temp ) )
	    temp = []
	if results == []:
	  return False
	return results
	
  def _printer( self, lvars, query ):
    '''Private method for constructing a result printing query.
    Usage: instance._printer( lvars, query )
    lvars - list of logical variables to print
    query - query containing the variables to be printed

    Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
    '''
    query = query[ :-1 ]
    elems = [ "writeln( res('''" + i + "'''," + i + ") )" for i in lvars ]
    printer = query + ',' + ','.join( elems ) + ',nl,fail.'
    return printer

eclipseprompt = '[\[]eclipse [0-9]+[\]][:] '
eclipseerror = 'Abort.*'

class ECLiPSeExecutableNotFound( Exception ):
  '''Exception raised if ECLiPSe-Prolog executable is not found on the specified path.'''
  pass

class ECLiPSeCompileError( Exception ): 
  '''Exception raised if loaded module has compile errors.'''
  pass

class ECLiPSeQueryError( Exception ): 
  '''Exception raised if query raises an error.'''
  pass

class eclipse:
  '''Python interface to ECLiPSe Prolog (http://eclipseclp.org)'''
  def __init__( self, path='eclipse', args='' ):
    '''Constructor method
    Usage: eclipse( path, args )
    path - path to ECLiPSe executable (default: 'eclipse')
    args - command line arguments (default: '')

    self.engine becomes pexpect spawn instance of ECLiPSe Prolog shell

    Raises: ECLiPSeExecutableNotFound'''
    try:
      self.engine = px.spawn( path + ' ' + args, timeout=5 )
    except px.ExceptionPexpect:
      raise ECLiPSeExecutableNotFound, 'ECLiPSe Prolog executable not found on the specified path.'
    self.engine.expect( eclipseprompt )
    
  def load( self, module ):
    '''Loads module into self.engine
    Usage: instance.load( path )
    path - path to module file

    Raises: ECLiPSeCompileError'''
    self.engine.sendline( "['" + module + "']." ) 
    index = self.engine.expect( [ eclipseerror, eclipseprompt ] )
    if index == 0:
      raise ECLiPSeCompileError, 'Error while compiling module "' + module + '". Error from ECLiPSe:\n' + self.engine.after 
    
  def query( self, query ):
    '''Queries current engine state
    Usage: instance.query( query )
    query - usual ECLiPSe Prolog query (example: 'likes( X, Y )')

    Returns:
      True - if yes/no query and answer is yes
      False - if yes/no query and answer is no
      List of dictionaries - if normal query. Dictionary keys are returned
      variable names. Example:
      >>> instance.query( 'likes( Person, Food )' )
      [{'Person': 'john', 'Food': 'curry'}, {'Person': 'sandy', 'Food': 'mushrooms'}]

    Raises: ECLiPSeQueryError'''
    query = query.strip()
    if query[ -1 ] != '.':
      query += '.'
    lvars = var_re.findall( query )
    lvars = list( set( lvars ) )
    if lvars == []: # yes/no query (no variables)
      self.engine.sendline( query )
      index = self.engine.expect( [ eclipseprompt, eclipseerror ] )
      if index == 1:
	raise ECLiPSeQueryError, 'Error while executing query "' + query + '". Error from ECLiPSe:\n' + self.engine.after
      else:
	if 'Yes' in self.engine.before:
	  return True
	else:
	  return False
    else: # normal query
      printer = self._printer( lvars, query )
      self.engine.sendline( printer )
      index = self.engine.expect( [ eclipseerror, eclipseprompt ] )
      if index == 0:
	raise ECLiPSeQueryError, 'Error while executing query "' + query + '". Error from ECLiPSe:\n' + self.engine.after
      else:
	res = res_re.findall( self.engine.before.split( ',nl,fail.\n' )[ -1 ] )
	results = []
	counter = 0
	temp = []
	for i in res:
	  counter += 1
	  temp.append( i )
	  if counter % len( lvars ) == 0:
	    results.append( dict( temp ) )
	    temp = []
	if results == []:
	  return False
	return results
	
  def _printer( self, lvars, query ):
    '''Private method for constructing a result printing query.
    Usage: instance._printer( lvars, query )
    lvars - list of logical variables to print
    query - query containing the variables to be printed

    Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
    '''
    query = query[ :-1 ]
    elems = [ "writeln( res('\\'" + i + "\\''," + i + ") )" for i in lvars ]
    printer = query + ',' + ','.join( elems ) + ',nl,fail.'
    return printer

flora2prompt = 'flora2 [?][-][ ]'
flora2error = '[+][+]Error.*'

fvar_re = re.compile( '[?][a-zA-Z0-9][a-zA-Z0-9_]*' )
fres_re = re.compile( "[?]([a-zA-Z0-9_]*) [=] ([^\r]+)" )


class Flora2ExecutableNotFound( Exception ):
  '''Exception raised if Flora2 executable is not found on the specified path.'''
  pass

class Flora2CompileError( Exception ): 
  '''Exception raised if loaded module has compile errors.'''
  pass

class Flora2QueryError( Exception ): 
  '''Exception raised if query raises an error.'''
  pass

class flora2:
  '''Python interface to Flora2 (http://flora.sf.net)'''
  def __init__( self, path='runflora', args='--nobanner --quietload' ):
    '''Constructor method
    Usage: flora2( path, args )
    path - path to Flora2 executable (default: 'runflora')
    args - command line arguments (default: '--nobanner --quietload')

    self.engine becomes pexpect spawn instance of Flora2 shell

    Raises: SWIExecutableNotFound'''
    try:
      self.engine = px.spawn( path + ' ' + args, timeout=5 )
      self.engine.expect( flora2prompt )
      self.engine.expect( flora2prompt )
    except px.ExceptionPexpect:
      raise SWIExecutableNotFound, 'Flora-2 executable not found on the specified path. Try using flora2( "/path/to/flora2/runflora" )'
   
  def load( self, module ):
    '''Loads module into self.engine
    Usage: instance.load( path )
    path - path to module file

    Raises: Flora2CompileError'''
    self.engine.sendline( "['" + module + "']." ) 
    index = self.engine.expect( [ flora2prompt, flora2error ] )
    if index == 1:
      raise Flora2CompileError, 'Error while compiling module "' + module + '". Error from Flora2:\n' + self.engine.after 
    
  def query( self, query ):
    '''Queries current engine state
    Usage: instance.query( query )
    query - usual Flora2 query (example: '?x[ likes->?y ]')

    Returns:
      True - if yes/no query and answer is yes
      False - if yes/no query and answer is no
      List of dictionaries - if normal query. Dictionary keys are returned
      variable names. Example:
      >>> instance.query( '?person[ likes->?food ]' )
      [{'person': 'john', 'food': 'curry'}, {'person': 'sandy', 'food': 'mushrooms'}]

    Raises: Flora2QueryError'''
    query = query.strip()
    if query[ -1 ] != '.':
      query += '.'
    lvars = fvar_re.findall( query )
    lvars = list( set( lvars ) )
    if lvars == []: # yes/no query (no variables)
      self.engine.sendline( query )
      index = self.engine.expect( [ flora2prompt, flora2error ] )
      if index == 1:
	raise Flora2QueryError, 'Error while executing query "' + query + '". Error from Flora2:\n' + self.engine.after
      else:
	if 'Yes' in self.engine.before:
	  return True
	else:
	  return False
    else: # normal query
      self.engine.sendline( query )
      index = self.engine.expect( [ flora2error, flora2prompt ] )
      if index == 0:
	raise Flora2QueryError, 'Error while executing query "' + query + '". Error from Flora2:\n' + self.engine.after
      else:
	res = fres_re.findall( self.engine.before )
	results = []
	counter = 0
	temp = []
	for i in res:
	  counter += 1
	  temp.append( i )
	  if counter % len( lvars ) == 0:
	    results.append( dict( temp ) )
	    temp = []
	return results

if __name__ == '__main__':
  x = xsb()
  x.load( 'test_xsb' )
  print x.query( 'dislikes( john, mushrooms )' )
  print x.query( 'likes( Person, Food )' )
  del x

  s = swipl()
  s.load( 'test_swi' )
  print s.query( 'dislikes( john, mushrooms )' )
  print s.query( 'likes( Person, Food )' )
  del s

  e = eclipse() 
  e.load( 'test_eclipse' )
  print e.query( 'dislikes( john, mushrooms )' )
  print e.query( 'likes( Person, Food )' )
  del e
  
  f = flora2()
  f.load( 'test_flora' )
  print f.query( 'john[ dislikes->mushrooms ]' )
  print f.query( '?person[ likes->?food ]' )
  del f
