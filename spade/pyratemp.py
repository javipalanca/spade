#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Small, simple and powerful template-engine for python.

This is a template-engine for python, which is very simple, easy to use,
small, fast, powerful and pythonic.

See documentation for a list of features, template-syntax etc.

:Version:   0.1.4 (2008-12-21)
:Status:    beta

:Usage:
    see class 'Template' and examples below.

:Example:

    quickstart::
        >>> t = Template("hello @!name!@")
        >>> print t(name="marvin")
        hello marvin

    generic usage::
        >>> t = Template("output is in Unicode äöü€")
        >>> t                                           #doctest: +ELLIPSIS
        <...Template instance at 0x...>
        >>> t()
        u'output is in Unicode \\xe4\\xf6\\xfc\\u20ac'
        >>> unicode(t)
        u'output is in Unicode \\xe4\\xf6\\xfc\\u20ac'

    with data::
        >>> t = Template("hello @!name!@", data={"name":"world"})
        >>> t()
        u'hello world'
        >>> t(name="worlds")
        u'hello worlds'

        # >>> t(note="data must be Unicode or ASCII", name=u"ä")
        # u'hello \\xe4\\xf6\\xe4\\u20ac'

    python-expressions::
        >>> Template('formatted: @! "%10.7f" % value !@')(value=3.141592653)
        u'formatted:  3.1415927'
        >>> Template("hello --@!name.upper().center(20)!@--")(name="world")
        u'hello --       WORLD        --'
        >>> Template("calculate @!var*5+7!@")(var=7)
        u'calculate 42'

    escaping::
        >>> t = Template("hello escaped @!name!@")
        >>> t(name='''<>&'" ''')
        u'hello escaped &lt;&gt;&amp;&#39;&quot; '
        >>> t = Template("hello unescaped $!name!$")
        >>> t(name='''<>&'" ''')
        u'hello unescaped <>&\\'" '
    
    result-encoding::
        # encode the unicode-object to your encoding with encode()
        >>> result = Template("hello äöü€")()
        >>> result
        u'hello \\xe4\\xf6\\xfc\\u20ac'
        >>> result.encode("utf-8")
        'hello \\xc3\\xa4\\xc3\\xb6\\xc3\\xbc\\xe2\\x82\\xac'
        >>> result.encode("ascii")
        Traceback (most recent call last):
          ...
        UnicodeEncodeError: 'ascii' codec can't encode characters in position 6-9: ordinal not in range(128)
        >>> result.encode("ascii", 'xmlcharrefreplace')
        'hello &#228;&#246;&#252;&#8364;'

    default-values::
        # non-existing variables raise an error
        >>> Template('hi @!optional!@')()
        Traceback (most recent call last):
          ...
        TemplateRenderError: Cannot eval expression 'optional' (NameError: name 'optional' is not defined)

        >>> t = Template('hi @!default("optional","anyone")!@')
        >>> t()
        u'hi anyone'
        >>> t(optional=None)
        u'hi anyone'
        >>> t(optional="there")
        u'hi there'

        # also in blocks
        >>> t = Template('<!--(if default("optional",False))-->yes<!--(else)-->no<!--(end)-->')
        >>> t()
        u'no'
        >>> t(optional=23)
        u'yes'
        
        # the 1st parameter can be any eval-expression
        >>> t = Template('@!default("5*var1+var2","missing variable")!@')
        >>> t(var1=10)
        u'missing variable'
        >>> t(var1=10, var2=2)
        u'52'

        # but make sure to put the expression in quotation marks, otherwise:
        >>> Template('@!default(optional,"fallback")!@')()
        Traceback (most recent call last):
          ...
        TemplateRenderError: Cannot eval expression 'default(optional,"fallback")' (NameError: name 'optional' is not defined)

    exists:
        >>> t = Template('<!--(if exists("foo"))-->YES<!--(else)-->NO<!--(end)-->')
        >>> t()
        u'NO'
        >>> t(foo=1)
        u'YES'
        >>> t(foo=None)       # note this difference to 'default()'
        u'YES'

:Note:

:Author:    Roland Koebler (rk at simple-is-better dot org)
:Copyright: 2007-2008 by Roland Koebler
:License:   MIT/X11-like, see __license__

:TODO:
    - enhance/extend escape()
    - speedup:
        - ? load/save parsed (marshal+check python-version)
        - ? psyco
        - ? escape -> C ?
        - ? compiler, (eval("\w+") -> data[..])

    - extensions:
        - ? set/define variables / capture output ?
          (i.e. <!--(set var)-->[1,2,3]<!--(end)-->)
        - ? filter ? (function over block)
"""

__version__ = "0.1.4"
__author__   = "Roland Koebler <rk at simple-is-better dot org>"
__license__  = """Copyright (c) 2007-2008 by Roland Koebler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE."""

#=========================================

import __builtin__, os
import re

#=========================================
# some useful functions

#----------------------
# string-position: i <-> row,col

def srow(string, i):
    """Get row/lineno of string[i].

    :Returns: row, starting at 1
    :Note:    This works for text-strings with '\\n' or '\\r\\n'.
    """
    return string.count('\n', 0, max(0, i)) + 1

def scol(string, i):
    """Get column of string[i].

    :Returns: column, starting at 1 (but may be <1 if i<0)
    :Note:    This works for text-strings with '\\n' or '\\r\\n'.
    """
    return i - string.rfind('\n', 0, max(0, i))

def sindex(string, row, col):
    """Get string-index of the character at row/lineno,col.
   
    :Parameters: row,col, starting at 1.
    :Returns:    i, starting at 0. (but may be <1 if row/col<0)
    :Note:       This works for text-strings with '\\n' or '\\r\\n'.
    """
    n = 0
    for _ in range(row-1):
        n = string.find('\n', n) + 1
    return n+col-1

#----------------------

def dictkeyclean(d):
    """Convert all keys of d to strings.
    """
    new_d = {}
    for k, v in d.iteritems():
        new_d[str(k)] = v
    return new_d

#----------------------
# escaping

(HTML, LATEX) = range(0, 2)
ESCAPE_SUPPORTED = {"NONE":None, "HTML":HTML, "LATEX":LATEX} #for error-/parameter-checking

def escape(s, format=HTML):
    """Replace special characters by their escape sequence.

    :Parameters:
        - `s`:      string or unicode-string to escape
        - `format`:
            - None:  nothing is replaced
            - HTML:  replace &<>'" by &...;
            - LATEX: replace #$%&_{}"\ (TODO! - this is very incomplete!)
    :Returns:
        the escaped string in unicode
    :TODO:  complete LaTeX-escaping
    """
    #note: if you have to make sure that every character gets replaced
    #      only once (and if you cannot achieve this with the following code),
    #      use something like u"".join([replacedict.get(c,c) for c in s])
    #      which is about 2-3 times slower (but maybe needs less memory)

    #note: this is one of the most time-consuming parts of the template.
    #      so maybe speed this up. (TODO)
    if format is None:
        pass
    elif format == HTML:
        s = s.replace(u"&", u"&amp;") # must be done first!
        s = s.replace(u"<", u"&lt;")
        s = s.replace(u">", u"&gt;")
        s = s.replace(u'"', u"&quot;")
        s = s.replace(u"'", u"&#39;")
    elif format == LATEX:
        #TODO: enhance this!
        #  which are the "reserved" characters for LaTeX?
        #  are there more than these?
        s = s.replace("\\", u"\\backslash{}")   #must be done first!
        s = s.replace("#",  u"\\#")
        s = s.replace("$",  u"\\$")
        s = s.replace("%",  u"\\%")
        s = s.replace("&",  u"\\&")
        s = s.replace("_",  u"\\_")
        s = s.replace("{",  u"\\{")
        s = s.replace("}",  u"\\}")
        s = s.replace('"',  u"{''}")    #TODO: should this be removed?
    else:
        raise ValueError('invalid format. (only None, HTML and LATEX are valid.)')
    return unicode(s)

#----------------------

def dummy(*args, **kwargs):
    """Dummy function, doing nothing.
    """
    pass

def dummy_raise(exception, value):
    """Dummy-function-creater.

    :Returns: dummy function, raising exception(value)
    """
    def mydummy(*args, **kwargs):
        raise exception(value)
    return mydummy


#=========================================

#-----------------------------------------
# Exceptions

class TemplateException(Exception):
    """Base class for template-exceptions."""
    pass

class TemplateParseError(TemplateException):
    """Template parsing failed."""
    def __init__(self, err, errpos):
        """:Parameters:
            - err:    error-message or exception to wrap
            - errpos: (filename,row,col) where the error occured.
        """
        self.err = err
        self.filename, self.row, self.col = errpos
        TemplateException.__init__(self)    #TODO: is this necessary?
    def __str__(self):
        if not self.filename:
            return "line %d, col %d: %s" % (self.row, self.col, str(self.err))
        else:
            return "file %s, line %d, col %d: %s" % (self.filename, self.row, self.col, str(self.err))

class TemplateSyntaxError(TemplateParseError, SyntaxError):
    """Template syntax-error."""
    pass

class TemplateIncludeError(TemplateParseError):
    """Template 'include' failed."""
    pass

class TemplateRenderError(TemplateException):
    """Template rendering failed."""
    pass

#-----------------------------------------
# Template + User-Interface

class TemplateBase:
    """Basic template-class.
    
    Used both for the template itself and for 'macro's ("subtemplates") in
    the template.
    """

    def __init__(self, parsetree, data, renderfunc):
        """Create the Template/Subtemplate/Macro.

        :Parameter:
            - parsetree:  parse-tree of the template/subtemplate/macro
            - data:       data to fill into the template by default (dictionary).
                          This data may later be overridden when rendering the template.
            - renderfunc: render-function
        """
        #TODO: parameter-checking...?
        self.parsetree = parsetree
        if isinstance(data, dict):
            self.data = data
        elif data is None:
            self.data = {}
        else:
            raise TypeError('"data" must be a dict (or None).')
        self.current_data = data
        self._render = renderfunc

    def __call__(self, **override):
        """Fill out/render the template.

        :Parameters: 
            - override: objects to add to the data-namespace, overriding
                        the "default"-data.
        :Returns:    the filled template (in unicode)
        :Note:       this is also called when invoking macros
                     (i.e. "$!mymacro()!$").
        """
        self.current_data = self.data.copy()
        self.current_data.update(override)  # note: current_data is used by _default etc.
        u = u"".join(self._render(self.parsetree, self.current_data))
        self.current_data = self.data       # restore current_data
        return _dontescape(u)               # (see class _dontescape)

    def __unicode__(self):
        """Alias for __call__()."""
        return self.__call__()
    def __str__(self):
        """Only here for completeness. Use __unicode__ instead!"""
        return self.__call__()


class Template(TemplateBase):
    """Template-User-Interface.

    :Usage:
        ::
            t = Template(...)  (<- see __init__)
            output = t(...)    (<- see TemplateBase.__call__)

    :Example:
        see module-docstring
    """

    def __init__(self, string=None,filename=None,parsetree=None, data=None, encoding='utf-8', escape=HTML ):
        """Load (+parse) a template.

        :Parameter:
            - string,filename,parsetree: a template-string,
                                         filename of a template to load,
                                         or a template-parsetree.
                                         (only one of these 3 is allowed)
            - data:       data to fill into the template by default (dictionary).
                          This data may later be overridden when rendering the template.
            - encoding: encoding of the template-files (only used for "filename")
            - escape: default-escaping for the template, may be overwritten by the template!
        """
        if [string, filename, parsetree].count(None) != 2:
            raise ValueError('only 1 of string,filename,parsetree is allowed.')
  
        u = None
        # load template
        if filename is not None:
            incl_load = FileLoader(os.path.dirname(filename), encoding).load
            u = incl_load(os.path.basename(filename))
        if string is not None:
            incl_load = dummy_raise(NotImplementedError, "'include' not supported for template-strings")
            u = StringLoader(encoding).load(string)

        # eval (incl. compile-cache)
        templateeval = TemplateEval()

        # parse
        if u is not None:
            p = Parser(loadfunc=incl_load, testexpr=templateeval.compile, escape=escape)
            parsetree = p.parse(u)
            del p

        # renderer
        renderer = Renderer(templateeval.eval)

        #create template
        TemplateBase.__init__(self, parsetree, data, renderer.render)


#-----------------------------------------
# Loader

class StringLoader:
    """Load a template from a string.

    Note that 'include' is not possible.
    """
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def load(self, string):
        """Return template-string as unicode."""
        if isinstance(string, unicode):
            u = string
        else:
            u = unicode(string, self.encoding)
        return u

class FileLoader:
    """Load template from a file.
    
    When loading a template from a file, it's possible to including other
    templates (by using 'include' in the template). But for simplicity
    and security, all included templates have to be in the same directory!
    (see 'allowed_path')
    """

    def __init__(self, allowed_path, encoding='utf-8'):
        """Init the loader.

        :Parameters:
            - allowed_path: path of the template-files
            - encoding: encoding of the template-files
        """
        if allowed_path and not os.path.isdir(allowed_path):
            #TODO: if this is not a dir, use dirname() ?
            raise ValueError("'allowed_path' has to be a directory.")
        self.path     = allowed_path
        self.encoding = encoding

    def load(self, filename):
        """Load a template from a file.

        Check if filename is allowed and return its contens in unicode.
        :Parameters:
            - filename: filename of the template without path
        :Returns:
            the contents of the template-file in unicode
        """
        if filename != os.path.basename(filename):
            raise ValueError("No pathname allowed (%s)." %(filename))
        filename = os.path.join(self.path, filename)

        f = open(filename, 'rb')
        string = f.read()
        f.close()

        u = unicode(string, self.encoding)

        return u

#-----------------------------------------
# Parser

class Parser(object):
    """Parse a template into a parse-tree.

    :TODO: describe the parse-tree
    """
    # template-syntax
    _comment_start = "#!"   #TODO: or <!--# ... #--> ?
    _comment_end   = "!#"
    _sub_start     = "$!"
    _sub_end       = "!$"
    _subesc_start  = "@!"
    _subesc_end    = "!@"
    _block_start   = "<!--("
    _block_end     = ")-->"

    # comment
    #   single-line, until end-tag or end-of-line.
    _strComment = r"""%s(?P<content>.*?)(?P<end>%s|\n|$)""" \
                    % (re.escape(_comment_start), re.escape(_comment_end))
    _reComment  = re.compile(_strComment, re.M)

    # escaped or unescaped substitution
    #   single-line, warn if no end-tag was found.
    _strSubstitution = r"""
                    (
                    %s\s*(?P<sub>.*?)\s*(?P<end>%s|$)       #substitution
                    |
                    %s\s*(?P<escsub>.*?)\s*(?P<escend>%s|$) #escaped substitution
                    )
                """ % (re.escape(_sub_start),    re.escape(_sub_end),
                       re.escape(_subesc_start), re.escape(_subesc_end))
    _reSubstitution = re.compile(_strSubstitution, re.X|re.M)

    # block
    #   - single-line, no nesting.
    #   or
    #   - multi-line, nested by whitespace indentation:
    #       * start- and end-tag of a block must have exactly the same indentation.
    #       * start- and end-tags of nested blocks should have a greater indentation.
    # NOTE: A single-line block must not start at beginning of the line with
    #       the same indentation as the enclosing multi-line block!
    #       note that "       " and "\t" are diffent, although they may cause the same "visual" indentation in an editor
    # TODO: maybe reduce re.escape-calls

    _strBlock = r"""
                    ^(?P<mEnd>[ \t]*)%send%s(?P<meIgnored>.*)\r?\n? # multi-line end  (^   <!--(end)-->IGNORED_TEXT\n)
                    |
                    (?P<sEnd>)%send%s                               # single-line end (<!--(end)-->)
                    |
                    (?P<sSpace>\s*)%s                               # single-line tag (no nesting)
                        (?P<sKeyw>\w+)[ \t]*(?P<sParam>.*?)
                    %s
                    (?P<sContent>.*?)
                    (?=(?:%s.*?%s.*?)??%send%s)
                    |
                                                                    # multi-line tag, nested by whitespace indentation
                    ^(?P<indent>[ \t]*)%s                           #   save indentation of start tag
                        (?P<mKeyw>\w+)\s*(?P<mParam>.*?)
                    %s(?P<mIgnored>.*)\r?\n
                    (?P<mContent>(?:.*\n)*?)
                    (?=(?P=indent)%s(?:.|\s)*?%s)                   #   match indentation
                """ % (re.escape(_block_start), re.escape(_block_end),
                       re.escape(_block_start), re.escape(_block_end),
                       re.escape(_block_start), re.escape(_block_end),
                       re.escape(_block_start), re.escape(_block_end),
                       re.escape(_block_start), re.escape(_block_end),
                       re.escape(_block_start), re.escape(_block_end),
                       re.escape(_block_start), re.escape(_block_end))
    _reBlock = re.compile(_strBlock, re.X|re.M)

    # "for"-block parameters: "var(,var)* in ..."
    _strForParam = r"""^(?P<names>\w+(?:\s*,\s*\w+)*)\s+in\s+(?P<iter>.+)$"""
    _reForParam  = re.compile(_strForParam)


    def __init__(self, loadfunc=None, testexpr=None, escape=HTML):
        """Init the parser.

        :Parameters:
            - loadfunc: function to load included templates
                        (i.e. FileLoader(...).load)
            - testexpr: function to test if a template-expressions is valid
                        (i.e. TempateEval().compile)
            - escape:   default-escaping (may be modified by the template <- TODO)
        """
        if loadfunc is None:
            self._load = dummy_raise(NotImplementedError, "'include' not supported")
        else:
            self._load = loadfunc
        if testexpr is None:
            self._testexprfunc = dummy
        else:
            try:    # test if testexpr() works
                testexpr("i==1")
            except Exception,err:
                raise ValueError("invalid 'testexpr' (%s)" %(err))
            self._testexprfunc = testexpr
        if escape not in ESCAPE_SUPPORTED.values():
            raise ValueError("unsupported 'escape' (%s)" %(escape))
        self.escape = escape
        self._block_cache = {}
        self._includestack = []

    def parse(self, template):
        """Parse a template.

        :Parameters:
            - template: template-unicode-string
        :Returns:    the resulting parse-tree
        :Raises:
            - TemplateSyntaxError: for template-syntax-errors
            - TemplateIncludeError: if template-inclusion failed
            - TemplateException
        """
        self._includestack = [(None, template)]   # for error-messages (_errpos)
        return self._parse(template)

    def _errpos(self, fpos):
        """Convert fpos to (filename,row,column) for error-messages."""
        filename, string = self._includestack[-1]
        return filename, srow(string, fpos), scol(string,fpos)

    def _testexpr(self, expr,  fpos=0):
        """Test a template-expression to detect errors."""
        try:
            self._testexprfunc(expr)
        except SyntaxError,err:
            raise TemplateSyntaxError(err, self._errpos(fpos))

    def _parse(self, template, fpos=0):
        """Recursive part of parse()."""
        def sub_append(parsetree, text, fpos=0):    # parse substitutions + append to parse-tree
            curr = 0
            for match in self._reSubstitution.finditer(text):
                start = match.start()
                if start > curr:
                    parsetree.append(("str", self._reComment.sub('', text[curr:start])))

                if match.group("sub") is not None:
                    if not match.group("end"):
                        raise TemplateSyntaxError("missing closing tag '%s' for '%s'" 
                                                  % (self._sub_end, match.group()), self._errpos(fpos+start))
                    if len(match.group("sub")) > 0:
                        self._testexpr(match.group("sub"), fpos+start)
                        parsetree.append(("sub", match.group("sub")))
                else:
                    assert(match.group("escsub") is not None)
                    if not match.group("escend"):
                        raise TemplateSyntaxError("missing closing tag '%s' for '%s'"
                                                  % (self._subesc_end, match.group()), self._errpos(fpos+start))
                    if len(match.group("escsub")) > 0:
                        self._testexpr(match.group("escsub"), fpos+start)
                        parsetree.append(("esc", self.escape, match.group("escsub")))

                curr = match.end()

            if len(text) > curr:
                parsetree.append(("str", self._reComment.sub('', text[curr:])))

        # blank out comments
        #   (so its content does not collide with other syntax)
        #   (and because removing them would falsify the character-position ("match.start()") of error-messages)
        template = self._reComment.sub(lambda match: "#!"+" "*len(match.group(1))+match.group(2), template)

        # init parser
        parsetree = []
        curr = 0            # current position (= end of previous block)
        block_type = None   # block type: if,for,macro,raw,...
        block_indent = None # None: single-line, >=0: multi-line

        # find blocks (+ cache them in self._block_cache)
        if template not in self._block_cache:
            self._block_cache[template] = list(self._reBlock.finditer(template))
        for match in self._block_cache[template]:
            start = match.start()
            if start > curr:    # process template-part before this block
                sub_append(parsetree, template[curr:start], fpos)

            # analyze block syntax (incl. error-checking and -messages)
            keyword = None
            block = match.groupdict()   #TODO: optimize?
            pos__ = fpos + start                # shortcut
            if   block["sKeyw"] is not None:    # single-line block tag
                block_indent = None
                keyword = block["sKeyw"]
                param   = block["sParam"]
                content = block["sContent"]
                if block["sSpace"]:             # restore spaces before start-tag
                    if len(parsetree) > 0 and parsetree[-1][0] == "str":
                        parsetree[-1] = ("str", parsetree[-1][1] + block["sSpace"])
                    else:
                        parsetree.append(("str", block["sSpace"]))
                pos_p = fpos + match.start("sParam")    # shortcuts
                pos_c = fpos + match.start("sContent")
            elif block["mKeyw"] is not None:    # multi-line block tag
                block_indent = len(block["indent"])
                keyword = block["mKeyw"]
                param   = block["mParam"]
                content = block["mContent"]
                pos_p = fpos + match.start("mParam")
                pos_c = fpos + match.start("mContent")
                if block["mIgnored"].strip():
                    raise TemplateSyntaxError("no code allowed after block-tag", self._errpos(fpos+match.start("mIgnored")))
            elif block["mEnd"] is not None:     # multi-line block end
                if block_type is None:
                    raise TemplateSyntaxError("no block to end here/invalid indent", self._errpos(pos__) )
                if block_indent != len(block["mEnd"]):
                    raise TemplateSyntaxError("invalid indent for end-tag", self._errpos(pos__) )
                if block["meIgnored"].strip():
                    raise TemplateSyntaxError("no code allowed after end-tag", self._errpos(fpos+match.start("meIgnored")))
                block_type = None
            elif block["sEnd"] is not None:     # single-line block end
                if block_type is None:
                    raise TemplateSyntaxError("no block to end here/invalid indent", self._errpos(pos__))
                if block_indent is not None:
                    raise TemplateSyntaxError("invalid indent for end-tag", self._errpos(pos__))
                block_type = None
            else:
                raise TemplateException("FATAL: block regexp error. please contact the author. (%s)" % match.group())
            
            # analyze block content (mainly error-checking and -messages)
            if keyword:
                keyword = keyword.lower()
                if   'for'   == keyword:
                    if block_type is not None:
                        raise TemplateSyntaxError("missing block-end-tag before new block at '%s'" %(match.group()), self._errpos(pos__))
                    block_type = 'for'
                    cond = self._reForParam.match(param)
                    if cond is None:
                        raise TemplateSyntaxError("invalid 'for ...' at '%s'" %(param), self._errpos(pos_p))
                    names = tuple(n.strip()  for n in cond.group("names").split(","))
                    self._testexpr(cond.group("iter"), pos_p+cond.start("iter"))
                    parsetree.append(("for", names, cond.group("iter"), self._parse(content, pos_c)))
                elif 'if'    == keyword:
                    if block_type is not None:
                        raise TemplateSyntaxError("missing block-end-tag before new block at '%s'" %(match.group()), self._errpos(pos__))
                    if not param:
                        raise TemplateSyntaxError("missing condition for 'if' at '%s'" %(match.group()), self._errpos(pos__))
                    block_type = 'if'
                    self._testexpr(param, pos_p)
                    parsetree.append(("if", param, self._parse(content, pos_c)))
                elif 'elif'  == keyword:
                    if block_type != 'if':
                        raise TemplateSyntaxError("'elif' may only appear after 'if' at '%s'" %(match.group()), self._errpos(pos__))
                    if not param:
                        raise TemplateSyntaxError("missing condition for 'elif' at '%s'" %(match.group()), self._errpos(pos__))
                    self._testexpr(param, pos_p)
                    parsetree.append(("elif", param, self._parse(content, pos_c)))
                elif 'else'  == keyword:
                    if block_type not in ['if', 'for']:
                        raise TemplateSyntaxError("'else' may only appear after 'if' of 'for' at '%s'" %(match.group()), self._errpos(pos__))
                    if param:
                        raise TemplateSyntaxError("'else' may not have parameters at '%s'" %(match.group()), self._errpos(pos__))
                    parsetree.append(("else", self._parse(content, pos_c)))
                elif 'macro' == keyword:
                    if block_type is not None:
                        raise TemplateSyntaxError("missing block-end-tag before new block '%s'" %(match.group()), self._errpos(pos__))
                    block_type = 'macro'
                    #TODO: make sure param is "\w+" ? (instead of ".+")
                    if not param:
                        raise TemplateSyntaxError("missing name for 'macro' at '%s'" %(match.group()), self._errpos(pos__))
                    #remove last newline
                    if len(content) > 0 and content[-1] == '\n':
                        content = content[:-1]
                    if len(content) > 0 and content[-1] == '\r':
                        content = content[:-1]
                    parsetree.append(("macro", param, self._parse(content, pos_c)))

                # parser-commands
                elif 'raw'   == keyword:
                    if block_type is not None:
                        raise TemplateSyntaxError("missing block-end-tag before new block '%s'" %(match.group()), self._errpos(pos__))
                    if param:
                        raise TemplateSyntaxError("'raw' may not have parameters at '%s'" %(match.group()), self._errpos(pos__))
                    block_type = 'raw'
                    parsetree.append(("str", content))
                elif 'include' == keyword:
                    if block_type is not None:
                        raise TemplateSyntaxError("missing block-end-tag before new block '%s'" %(match.group()), self._errpos(pos__))
                    if param:
                        raise TemplateSyntaxError("'include' may not have parameters at '%s'" %(match.group()), self._errpos(pos__))
                    block_type = 'include'
                    try:
                        u = self._load(content.strip())
                    except Exception,err:
                        raise TemplateIncludeError(err, self._errpos(pos__))
                    self._includestack.append((content.strip(), u))  # current filename/template for error-msg.
                    p = self._parse(u)
                    self._includestack.pop()
                    parsetree.extend(p)
                elif 'set_escape' == keyword:
                    if block_type is not None:
                        raise TemplateSyntaxError("missing block-end-tag before new block '%s'" %(match.group()), self._errpos(pos__))
                    if param:
                        raise TemplateSyntaxError("'set_escape' may not have parameters at '%s'" %(match.group()), self._errpos(pos__))
                    block_type = 'set_escape'
                    esc = content.strip().upper()
                    if esc in ESCAPE_SUPPORTED:
                        self.escape = ESCAPE_SUPPORTED[esc]
                    else:
                        raise TemplateSyntaxError("unsupported escape '%s'" %(esc), self._errpos(pos__))
                #TODO: add 'charset' block ?
                else:
                    raise TemplateSyntaxError("invalid keyword '%s'" %(keyword), self._errpos(pos__))
            curr = match.end()

        if block_type is not None:
            raise TemplateSyntaxError("missing end-tag", self._errpos(pos__))

        if len(template) > curr:            #interpolate template-part after last block
            sub_append(parsetree, template[curr:], fpos)

        return parsetree

#-----------------------------------------
# Evaluation

# some checks
assert len(eval("dir()", {'__builtins__':{'dir':dir}})) == 1, "FATAL: eval does not work as expected (%s)."
assert compile("0 .__class__", "<string>", "eval").co_names == ('__class__',), "FATAL: compile does not work as expected."

class PseudoSandbox:
    """A pseudo-eval-sandbox.

    - Allow only some of the builtin python-functions
      (see eval_allowed_globals), which are considered "save".
    - Forbid names beginning with "_".
      This is to prevent things like '0 .__class__', with which you could
      easily break out of a "sandbox".

    Note that this is no real sandbox!
    Don't use it for untrusted code!!
    """

    eval_allowed_globals = {
            "True"      : __builtin__.True,
            "False"     : __builtin__.False,
            "None"      : __builtin__.None,

            "abs"       : __builtin__.abs,
            "chr"       : __builtin__.chr,
            "cmp"       : __builtin__.cmp,
            "divmod"    : __builtin__.divmod,
            "hash"      : __builtin__.hash,
            "hex"       : __builtin__.hex,
            "len"       : __builtin__.len,
            "max"       : __builtin__.max,
            "min"       : __builtin__.min,
            "oct"       : __builtin__.oct,
            "ord"       : __builtin__.ord,
            "pow"       : __builtin__.pow,
            "range"     : __builtin__.range,
            "round"     : __builtin__.round,
            "sorted"    : __builtin__.sorted,
            "sum"       : __builtin__.sum,
            "unichr"    : __builtin__.unichr,
            "zip"       : __builtin__.zip,

            "bool"      : __builtin__.bool,
            "complex"   : __builtin__.complex,
            "dict"      : __builtin__.dict,
            "enumerate" : __builtin__.enumerate,
            "float"     : __builtin__.float,
            "int"       : __builtin__.int,
            "list"      : __builtin__.list,
            "long"      : __builtin__.long,
            "reversed"  : __builtin__.reversed,
            "str"       : __builtin__.str,
            "tuple"     : __builtin__.tuple,
            "unicode"   : __builtin__.unicode,
            "xrange"    : __builtin__.xrange,
            #TODO: ? __builtin__.frozenset, .set, .slice
            #      ? .filter, .iter, .map, .reduce
            }

    def __init__(self):
        self._compile_cache = {}
        self.locals = None

    def register(self, name, obj):
        """Add an object to the "allowed eval-globals".

        Mainly useful to add user-defined functions to the pseudo-sandbox.
        """
        self.eval_allowed_globals[name] = obj

    def compile(self, expr):
        """Compile a python-eval-expression.

        - Use a compile-cache
        - Raise an NameError if expr contains a name beginning with '_'.
        
        :Returns: the compiled expr
        :Raises: SyntaxError for compile-errors,
                 NameError if expr contains a name beginning with '_'
        """
        if expr not in self._compile_cache:
            c = compile(expr, "", "eval")
            for i in c.co_names:    #prevent breakout via new-style-classes
                if i[0] == '_':
                    raise NameError("name '%s' is not allowed" %(i))
            self._compile_cache[expr] = c
        return self._compile_cache[expr]

    def eval(self, expr, locals):
        """Eval a python-eval-expression.
        
        Uses the compile-cache.
        """
        self.locals = locals    # used by user-defined functions, i.e. default()
        if expr not in self._compile_cache:
            self._compile_cache[expr] = self.compile(expr)
        compiled = self._compile_cache[expr]

        return eval(compiled, {"__builtins__":self.eval_allowed_globals}, locals)



class TemplateEval(PseudoSandbox):
    """PseudoSandbox with some additional functions, which are useful
    in the template.

    Additional functions:
    - "default" calls _default()
    - "exists": calls _exists()
    """

    def __init__(self):
        PseudoSandbox.__init__(self)
        self.register("default", self._default)
        self.register("exists",  self._exists)

    def _default(self, expr, default=None):
        """Return the eval-result of expr or a "fallback"-value.

        Use this in the template to use default-values for optional data.
        The default-value is used if 'expr' does not exist/is invalid/results in None.

        :Note: the variable-name has to be quoted! (like in eval)

        :Example:
            ::
                @! default("optional_var","fallback_value") !@
                <!--(if default("optional",False))-->"YES"<!--(else)-->"NO"<!--(end)-->
                <!--(for i in default("optional_list",[]))-->
        """
        try:
            r = self.eval(expr, self.locals)
            if r is None:
                return default
            return r
        #TODO: which exceptions should be catched here?
        except Exception: #(NameError,IndexError,KeyError):
            return default

    def _exists(self, varname):
        """Test if a variable exists.

        This tests if 'varname' exists in the current locals-namespace.

        :Note: the variable-name has to be quoted! (like in eval)

        This only works for single variable names. If you want to test
        complicated expressions, use i.e. _default.
        (i.e. _default("expr",False))
        """
        return (varname in self.locals)

#-----------------------------------------
# Renderer

class _dontescape(unicode):
    """Unicode-string which should not be escaped.

    If ``isinstance(object,_dontescape)``, then don't escape it in @!...!@.
    It's useful for not double-escaping macros, and it's automatically
    used for macros/subtemplates.

    :Note: This only works if the object is used on its own in @!...!@.
           It i.e. does not work in @! object*2 !@ or @! object + "hi" !@.
    """
    __slots__ = []


class Renderer(object):
    """Render a template-parse-tree."""

    def __init__(self, evalfunc):
        """Init the renderer.

        :Parameter:
            - evalfunc: function for template-expression-evaluation (i.e. TemplateEval().eval)
        """
        #TODO test evalfunc
        self.evalfunc = evalfunc

    def _eval(self, expr, data):
        """evalfunc with error-messages"""
        try:
            return self.evalfunc(expr, data)
        # TODO: any other errors to catch here?
        except (TypeError,NameError,IndexError,KeyError,AttributeError, SyntaxError), err:
            raise TemplateRenderError("Cannot eval expression '%s' (%s: %s)" %(expr, err.__class__.__name__, err))

    def render(self, parsetree, data):
        """Render a parse-tree of a template.

        :Parameter:
            - parsetree: the parse-tree
            - data:      the data to fill into the template (dictionary)
        :Returns:   the rendered output-unicode-string
        :Raises:    TemplateRenderError
        """
        _eval = self._eval  # shortcut
        output = []

        do_else = False     # use else/elif-branch?
        if parsetree is None:
            return ""
        for elem in parsetree:
            if   "str"   == elem[0]:
                output.append(elem[1])
            elif "sub"   == elem[0]:
                output.append(unicode(_eval(elem[1], data)))
            elif "esc"   == elem[0]:
                obj = _eval(elem[2], data)
                #prevent double-escape
                if isinstance(obj, _dontescape) or isinstance(obj, TemplateBase):
                    output.append(unicode(obj))
                else:
                    output.append(escape(unicode(obj), elem[1]))
            elif "for"   == elem[0]:
                do_else = True
                (names, iterable) = elem[1:3]
                try:
                    loop_iter = iter(_eval(iterable, data))
                except TypeError:
                    raise TemplateRenderError("Cannot loop over '%s'." % iterable)
                for i in loop_iter:
                    do_else = False
                    if len(names) == 1:
                        data[names[0]] = i
                    else:
                        data.update(zip(names, i))   #"for a,b,.. in list"
                    output.extend(self.render(elem[3], data))
            elif "if"    == elem[0]:
                do_else = True
                if _eval(elem[1], data):
                    do_else = False
                    output.extend(self.render(elem[2], data))
            elif "elif"  == elem[0]:
                if do_else and _eval(elem[1], data):
                    do_else = False
                    output.extend(self.render(elem[2], data))
            elif "else"  == elem[0]:
                if do_else:
                    do_else = False
                    output.extend(self.render(elem[1], data))
            elif "macro" == elem[0]:
                data[elem[1]] = TemplateBase(elem[2], data, self.render)
            else:
                raise TemplateRenderError("invalid parse-tree (%s)" %(elem))

        return output

#=========================================
#----------------------
#doctest

def _doctest():
    """doctest this module."""
    import doctest
    doctest.testmod()

#----------------------
if __name__ == '__main__':
    _doctest()

#=========================================

