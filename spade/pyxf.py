# -*- coding: utf-8 -*-
__doc__ = ''' Python interface to XSB Prolog, SWI Prolog, ECLiPSe Prolog and Flora2
 by Markus Schatten <markus_dot_schatten_at_foi_dot_hr>
 Faculty of Organization and Informatics,
 Varazdin, Croatia, 2011 - now

 Shamelessly using:
 http://code.activestate.com/recipes/440554/ (r10)

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

__version__ = '1.0.4'

import re
import os
import subprocess
import errno
import time
import sys
import shlex

PIPE = subprocess.PIPE

if subprocess.mswindows:
	from win32file import ReadFile, WriteFile
	from win32pipe import PeekNamedPipe
	import msvcrt
else:
	import select
	import fcntl

class Spawner(subprocess.Popen):
	'''Simple platform independent spawner for shell-like processes
	(inherits subprocess.Popen)

	Based on:

	http://code.activestate.com/recipes/440554/ (r10)
	'''
	message = "Other end disconnected!"

	def recv(self, maxsize=None):
		'''receive from stdout
		Usage: instance.recv( maxsize )
		maxsize - optional number of bytes to receive'''
		return self._recv('stdout', maxsize)
	
	def recv_err(self, maxsize=None):
		'''receive from sterr
		Usage: instance.recv_err( maxsize )
		maxsize - optional number of bytes to receive'''
		return self._recv('stderr', maxsize)

	def send_recv(self, input='', maxsize=None):
		'''Send input, and receive both stdout and stderr
		Usage: instance.send_recv( input, maxsize )
		input - optional input string
		maxsize - optional number of bytes to receive'''
		return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

	def get_conn_maxsize(self, which, maxsize):
		'''Get the maximal size of connection buffer
		Usage: instance.get_conn_maxsize( which, maxsize )
		which - connection to check
		maxsize - maxsize as wanted by the process'''
		if maxsize is None:
			maxsize = 1024
		elif maxsize < 1:
			maxsize = 1
		return getattr(self, which), maxsize
	
	def _close(self, which):
		'''Private method to close the process connection
		Usage: instance._close( which )
		which - connection to close'''
		getattr(self, which).close()
		setattr(self, which, None)
	
	def get(self, t=.1, e=1, tr=5):
		'''Get the output (stdin + stderr) after a sent line
		Usage: instance.get( t, e, tr )
		t - timeout in seconds (default 0.2)
		e - raise exceptions? (default: 1 )
		tr - number of tries (default=5)'''
		if tr < 1:
			tr = 1
		x = time.time()+t
		y = []
		r = ''
		pr = self.recv
		while time.time() < x or r:
			r = pr()
			if r is None:
				if e:
					raise Exception(self.message)
				else:
					break
			elif r:
				y.append(r)
			else:
				time.sleep(max((x-time.time())/tr, 0))
		res = ''.join(y) + self.endline
		pr = self.recv_err
		if tr < 1:
			tr = 1
		x = time.time()+t
		y = []
		r = ''
		while time.time() < x or r:
			r = pr()
			if r is None:
				if e:
					raise Exception(self.message)
				else:
					break
			elif r:
				y.append(r)
			else:
				time.sleep(max((x-time.time())/tr, 0))
		res += ''.join(y)
		return res
		
	def send_all(self, data):
		'''Send data to the process
		Usage: instance.send_all( data )
		data - data to be transmitted'''
		while len(data):
			sent = self.send(data)
			if sent is None:
				raise Exception(self.message)
			data = buffer(data, sent)
	
	def sendline(self, line):
		'''Send data to the process with a platform dependend newline
		character which is appended to the data
		Usage: instance.sendline( line )
		line - string (without newline) to be sent to the process'''
		self.send_all(line + self.endline)

	if subprocess.mswindows:
		'''Windows specific attributes and methods'''
		endline = "\r\n"

		def send(self, input):
			'''Send input to stdin
			Usage: instance.send( input )
			input - input to be sent'''
			if not self.stdin:
				return None

			try:
				x = msvcrt.get_osfhandle(self.stdin.fileno())
				(errCode, written) = WriteFile(x, input)
			except ValueError:
				return self._close('stdin')
			except (subprocess.pywintypes.error, Exception), why:
				if why[0] in (109, errno.ESHUTDOWN):
					return self._close('stdin')
				raise

			return written

		def _recv(self, which, maxsize):
			'''Private method for receiving data from process
			Usage: instance( which, maxsize (
			which - connection to receive output from
			maxsize - maximm size of buffer to be received'''
			conn, maxsize = self.get_conn_maxsize(which, maxsize)
			if conn is None:
				return None
			
			try:
				x = msvcrt.get_osfhandle(conn.fileno())
				(read, nAvail, nMessage) = PeekNamedPipe(x, 0)
				if maxsize < nAvail:
					nAvail = maxsize
				if nAvail > 0:
					(errCode, read) = ReadFile(x, nAvail, None)
			except ValueError:
				return self._close(which)
			except (subprocess.pywintypes.error, Exception), why:
				if why[0] in (109, errno.ESHUTDOWN):
					return self._close(which)
				raise
			
			if self.universal_newlines:
				read = self._translate_newlines(read)
			return read

	else:
		'''*NIX specific attributes and methods'''
		endline = "\n"

		def send(self, input):
			'''Send input to stdin
			Usage: instance.send( input )
			input - input to be sent'''
			if not self.stdin:
				return None

			if not select.select([], [self.stdin], [], 0)[1]:
				return 0

			try:
				written = os.write(self.stdin.fileno(), input)
			except OSError, why:
				if why[0] == errno.EPIPE: #broken pipe
					return self._close('stdin')
				raise

			return written

		def _recv(self, which, maxsize):
			'''Private method for receiving data from process
			Usage: instance( which, maxsize (
			which - connection to receive output from
			maxsize - maximm size of buffer to be received'''
			conn, maxsize = self.get_conn_maxsize(which, maxsize)
			if conn is None:
				return None
			
			flags = fcntl.fcntl(conn, fcntl.F_GETFL)
			if not conn.closed:
				fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)
			
			try:
				if not select.select([conn], [], [], 0)[0]:
					return ''
				
				r = conn.read(maxsize)
				if not r:
					return self._close(which)
	
				if self.universal_newlines:
					r = self._translate_newlines(r)
				return r
			finally:
				if not conn.closed:
					fcntl.fcntl(conn, fcntl.F_SETFL, flags)


xsberror = re.compile('[+][+]Error.*')

var_re = re.compile('[^a-zA-Z0-9_]([A-Z][a-zA-Z0-9_]*)')
res_re = re.compile("res[\(]'([A-Z][a-zA-Z0-9_]*)',[ ]?(.*)[\)]")


class XSBExecutableNotFound(Exception):
	'''Exception raised if XSB executable is not found on the specified path.'''
	pass


class XSBCompileError(Exception):
	'''Exception raised if loaded module has compile errors.'''
	pass


class XSBQueryError(Exception):
	'''Exception raised if query raises an error.'''
	pass


class xsb:
	'''Python interface to XSB Prolog (http://xsb.sf.net)'''
	def __init__(self, path='xsb', args='--nobanner --quietload'):
		'''Constructor method
		Usage: xsb( path, args )
		path - path to XSB executable (default: 'xsb')
		args - command line arguments (default: '--nobanner --quietload')

		self.engine becomes pexpect spawn instance of XSB Prolog shell

		Raises: XSBExecutableNotFound'''
		try:
			self.engine = Spawner(shlex.split(path + ' ' + args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
		except:
			raise XSBExecutableNotFound('XSB executable not found on the specified path. Try using xsb( "/path/to/XSB/bin/xsb" )')

	def load(self, module):
		'''Loads module into self.engine
		Usage: instance.load( path )
		path - path to module file

		Raises: XSBCompileError'''
		self.engine.sendline("['" + module + "'].")
		res = self.engine.get() 
		if xsberror.findall(res) != []:
			raise XSBCompileError('Error while compiling module "' + module + '". Error from XSB:\n' + res)

	def query(self, query):
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
		if query[-1] != '.':
			query += '.'
		lvars = var_re.findall(query)
		lvars = list(set(lvars))
		if lvars == []:  # yes/no query (no variables)
			self.engine.sendline(query)
			res = self.engine.get()
			if xsberror.findall(res) != []:
				raise XSBQueryError('Error while executing query "' + query + '". Error from XSB:\n' + res)
			else:
				if 'yes' in res:
					return True
				else:
					return False
		else:  # normal query
			printer = self._printer(lvars, query)
			self.engine.sendline(printer)
			res = self.engine.get() 
			if xsberror.findall(res) != []:
				raise XSBQueryError('Error while executing query "' + query + '". Error from XSB:\n' + res)
			else:
				res = res_re.findall(res)
				results = []
				counter = 0
				temp = []
				for i in res:
					counter += 1
					temp.append(i)
					if counter % len(lvars) == 0:
						results.append(dict(temp))
						temp = []
				if results == []:
					return False
				return results

	def _printer(self, lvars, query):
		'''Private method for constructing a result printing query.
		Usage: instance._printer( lvars, query )
		lvars - list of logical variables to print
		query - query containing the variables to be printed

		Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
		'''
		query = query[:-1]
		elems = ["writeln( res('''" + i + "'''," + i + ") )" for i in lvars]
		printer = query + ',' + ','.join(elems) + ',nl,fail.'
		return printer

	def __del__(self):
		'''Clean up on instance destruction and stop the engine process
		Usage: del instance'''
		try:
			self.engine.sendline('halt.')
			self.engine.get( e=0 )
			self.engine.wait()
		except:
			# connection to engine already lost, do nothing
			pass

swierror = re.compile('ERROR.*')


class SWIExecutableNotFound(Exception):
	'''Exception raised if SWI-Prolog executable is not found on the specified path.'''
	pass


class SWICompileError(Exception):
	'''Exception raised if loaded module has compile errors.'''
	pass


class SWIQueryError(Exception):
	'''Exception raised if query raises an error.'''
	pass


class swipl:
	'''Python interface to SWI Prolog (http://www.swi-prolog.org)'''
	def __init__(self, path='/usr/bin/swipl', args='-q +tty'):
		'''Constructor method
		Usage: swipl( path, args )
		path - path to SWI executable (default: 'swipl')
		args - command line arguments (default: '-q +tty')

		self.engine becomes pexpect spawn instance of SWI Prolog shell

		Raises: SWIExecutableNotFound'''
		try:
			self.engine = Spawner(shlex.split(path + ' ' + args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
		except:
			raise SWIExecutableNotFound('SWI-Prolog executable not found on the specified path. Try installing swi-prolog or using swipl( "/path/to/swipl" )')

	def load(self, module):
		'''Loads module into self.engine
		Usage: instance.load( path )
		path - path to module file

		Raises: SWICompileError'''
		self.engine.sendline("['" + module + "'].")
		res = self.engine.get() 
		if swierror.findall(res) != []:
			raise SWICompileError('Error while compiling module "' + module + '". Error from SWI:\n' + res)

	def query(self, query):
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
		if query[-1] != '.':
			query += '.'
		lvars = var_re.findall(query)
		lvars = list(set(lvars))
		if lvars == []:  # yes/no query (no variables)
			self.engine.sendline(query)
			res = self.engine.get() 
			if swierror.findall(res) != []:
				raise SWIQueryError('Error while executing query "' + query + '". Error from SWI:\n' + res)
			else:
				if 'true' in res:
					return True
				else:
					return False
		else:  # normal query
			printer = self._printer(lvars, query)
			self.engine.sendline(printer)
			res = self.engine.get()
			if swierror.findall(res) != []:
				raise SWIQueryError('Error while executing query "' + query + '". Error from SWI:\n' + res)
			else:
				res = res_re.findall(res)
				results = []
				counter = 0
				temp = []
				for i in res:
					counter += 1
					temp.append(i)
					if counter % len(lvars) == 0:
						results.append(dict(temp))
						temp = []
				if results == []:
					return False
				return results

	def _printer(self, lvars, query):
		'''Private method for constructing a result printing query.
		Usage: instance._printer( lvars, query )
		lvars - list of logical variables to print
		query - query containing the variables to be printed

		Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
		'''
		query = query[:-1]
		elems = ["writeln( res('''" + i + "'''," + i + ") )" for i in lvars]
		printer = query + ',' + ','.join(elems) + ',nl,fail.'
		return printer

	def __del__(self):
		'''Clean up on instance destruction and stop the engine process
		Usage: del instance'''
		try:
			self.engine.sendline('halt.')
			self.engine.get( e=0 )
			self.engine.wait()
		except:
			# connection to engine already lost, do nothing
			pass

eclipseerror = re.compile('Abort.*')


class ECLiPSeExecutableNotFound(Exception):
	'''Exception raised if ECLiPSe-Prolog executable is not found on the specified path.'''
	pass


class ECLiPSeCompileError(Exception):
	'''Exception raised if loaded module has compile errors.'''
	pass


class ECLiPSeQueryError(Exception):
	'''Exception raised if query raises an error.'''
	pass

class eclipse:
	'''Python interface to ECLiPSe Prolog (http://eclipseclp.org)'''
	def __init__(self, path='eclipse', args=''):
		'''Constructor method
		Usage: eclipse( path, args )
		path - path to ECLiPSe executable (default: 'eclipse')
		args - command line arguments (default: '')

		self.engine becomes pexpect spawn instance of ECLiPSe Prolog shell

		Raises: ECLiPSeExecutableNotFound'''
		try:
			self.engine = Spawner(shlex.split(path + ' ' + args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
		except:
			raise ECLiPSeExecutableNotFound('ECLiPSe Prolog executable not found on the specified path. Try installing elipse-prolog or using eclipse( "/path/to/eclipse" )')

	def load(self, module):
		'''Loads module into self.engine
		Usage: instance.load( path )
		path - path to module file

		Raises: ECLiPSeCompileError'''
		self.engine.sendline("['" + module + "'].")
		res = self.engine.get(t=.25)
		if eclipseerror.findall(res) != []:
			raise ECLiPSeCompileError('Error while compiling module "' + module + '". Error from ECLiPSe:\n' + res)

	def query(self, query):
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
		if query[-1] != '.':
			query += '.'
		lvars = var_re.findall(query)
		lvars = list(set(lvars))
		if lvars == []:  # yes/no query (no variables)
			self.engine.sendline(query)
			res = self.engine.get(t=.25)
			if eclipseerror.findall(res) != []:
				raise ECLiPSeQueryError('Error while executing query "' + query + '". Error from ECLiPSe:\n' + res)
			else:
				if 'Yes' in res:
					return True
				else:
					return False
		else:  # normal query
			printer = self._printer(lvars, query)
			self.engine.sendline(printer)
			res = self.engine.get(t=.25)
			if eclipseerror.findall(res) != []:
				raise ECLiPSeQueryError('Error while executing query "' + query + '". Error from ECLiPSe:\n' + res)
			else:
				res = res_re.findall(res)
				results = []
				counter = 0
				temp = []
				for i in res:
					counter += 1
					temp.append(i)
					if counter % len(lvars) == 0:
						results.append(dict(temp))
						temp = []
				if results == []:
					return False
				return results

	def _printer(self, lvars, query):
		'''Private method for constructing a result printing query.
		Usage: instance._printer( lvars, query )
		lvars - list of logical variables to print
		query - query containing the variables to be printed

		Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
		'''
		query = query[:-1]
		elems = ["writeln( res('\\'" + i + "\\''," + i + ") )" for i in lvars]
		printer = query + ',' + ','.join(elems) + ',nl,fail.'
		return printer

	def __del__(self):
		'''Clean up on instance destruction and stop the engine process
		Usage: del instance'''
		try:
			self.engine.sendline('halt.')
			self.engine.get( e=0 )
			self.engine.wait()
		except:
			# connection to engine already lost, do nothing
			pass

flora2error = re.compile('[+][+]Error.*')

fvar_re = re.compile('[?][a-zA-Z0-9][a-zA-Z0-9_]*')
fres_re = re.compile("[?]([a-zA-Z0-9_]*) [=] ([^\r\n]+)")


class Flora2ExecutableNotFound(Exception):
	'''Exception raised if Flora2 executable is not found on the specified path.'''
	pass


class Flora2CompileError(Exception):
	'''Exception raised if loaded module has compile errors.'''
	pass


class Flora2QueryError(Exception):
	'''Exception raised if query raises an error.'''
	pass


class flora2:
	'''Python interface to Flora2 (http://flora.sf.net)'''
	def __init__(self, path='runflora', args='--nobanner --quietload'):
		'''Constructor method
		Usage: flora2( path, args )
		path - path to Flora2 executable (default: 'runflora')
		args - command line arguments (default: '--nobanner --quietload')

		self.engine becomes pexpect spawn instance of Flora2 shell

		Raises: SWIExecutableNotFound'''
		try:
			self.engine = Spawner(shlex.split(path + ' ' + args), stdin=PIPE, stdout=PIPE, stderr=PIPE)
		except:
			raise Flora2ExecutableNotFound('Flora-2 executable not found on the specified path. Try using flora2( "/path/to/flora2/runflora" )')

	def load(self, module, into=None):
		'''Loads module into self.engine
		Usage: instance.load( path )
		path - path to module file
		into - load into module

		Raises: Flora2CompileError'''
		if into:
			self.engine.sendline("['" + module + "'>>'" + into + "'].")
		else:
			self.engine.sendline("['" + module + "'].")
		res = self.engine.get(t=.5)
		if flora2error.findall(res) != []:
			raise Flora2CompileError('Error while compiling module "' + module + '". Error from Flora2:\n' + res)

	def query(self, query):
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
		if query[-1] != '.':
			query += '.'
		lvars = fvar_re.findall(query)
		lvars = list(set(lvars))
		if lvars == []:  # yes/no query (no variables)
			self.engine.sendline(query)
			res = self.engine.get(t=.2, tr=10)
			if flora2error.findall(res) != []:
				raise Flora2QueryError('Error while executing query "' + query + '". Error from Flora2:\n' + res)
			else:
				if 'Yes' in res:
					return True
				else:
					return False
		else:  # normal query
			self.engine.sendline(query)
			res = self.engine.get(t=.2, tr=10)
			if flora2error.findall(res) != []:
				raise Flora2QueryError('Error while executing query "' + query + '". Error from Flora2:\n' + res)
			else:
				res = fres_re.findall(res)
				results = []
				counter = 0
				temp = []
				for i in res:
					counter += 1
					temp.append(i)
					if counter % len(lvars) == 0:
						results.append(dict(temp))
						temp = []
				return results

	def __del__(self):
		'''Clean up on instance destruction and stop the engine process
		Usage: del instance'''
		try:
			self.engine.sendline('_halt.')
			self.engine.get( e=0 )
			self.engine.wait()
		except:
			# connection to engine already lost, do nothing
			pass

if __name__ == '__main__':
	
	x = xsb()
	x.load('../test/logic/test_xsb')
	print x.query('dislikes( john, mushrooms )')
	print x.query('likes( Person, Food )')
	del x

	print "======="

	s = swipl()
	s.load('../test/logic/test_swi')
	print s.query('dislikes( john, mushrooms )')
	print s.query('likes( Person, Food )')
	#print s.query('?Bla(bla)')
	del s

	print "======="
	
	e = eclipse()
	e.load('../test/logic/test_eclipse')
	print e.query('dislikes( john, mushrooms )')
	print e.query('likes( Person, Food )')
	del e

	print "======="
	
	f = flora2()
	f.load('../test/logic/test_flora')
	print f.query('john[ dislikes->mushrooms ]')
	print f.query('?person[ likes->?food ]')
	del f
