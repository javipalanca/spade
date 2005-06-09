#!/usr/bin/python

import jabber
import xmlstream

USE_COLOR = 1

def colorize(txt, col):
    """Return colorized text"""
    if not USE_COLOR: return txt ## DJ - just incase it breaks your terms ;) ##
    cols = { 'red':1, 'green':2, 'yellow':3, 'blue':4}
    initcode = '\033[;3'
    endcode  = '\033[0m'
    if type(col) == type(1):
        return initcode + str(col) + 'm' + txt + endcode
    try: return initcode + str(cols[col]) + 'm' + txt + endcode
    except: return txt

def colorXML(n,depth=0):
	m = u""
	for i in range(0,depth):
		m = m + "\t"
	m = m + colorize("<",'green')+colorize(n.getName(),'red')
	for k,v in n.attrs.items():
		m = m + " " + colorize(str(k),'yellow') + "=" + colorize(str(v),'blue')
	m = m + colorize(">",'green')
	if n.getData():
		if len(n.kids) == 0:  # No children, no indentation
			m = m + str(n.getData())
		else:
			m = m + "\n"
			for i in range(0,depth):
				m = m + "\t"
			m = m + str(n.getData())
	for child in n.kids:
		m = m + "\n"
		m = m + colorXML(child,depth+1)
	if len(n.kids) != 0:  # No children, no indentation
		m = m + "\n"
		for i in range(0,depth):
			m = m + "\t"
	m = m + colorize("</",'green') + colorize(n.getName(),'red') + colorize(">",'green')
	return m

def colorXMLraw(raw,depth=0):
	n = xmlstream.Node("bla")
	n.insertXML(raw)
	for x in n.kids:
		m = colorXML(x) 
	return m

#~ x = xmlstream.Node("message")
#~ x.insertData("BLABLA")
#~ x.putAttr("type","fipper")
#~ y = xmlstream.Node("child")
#~ y.insertData("BLOBLOBLO")
#~ x.insertNode(y)
#~ y.setParent(x)
#~ y2 = xmlstream.Node("otro_mas")
#~ y2.putAttr("asi","asa")
#~ x.insertNode(y2)
#~ z = xmlstream.Node("tercero")
#~ z.insertData("JAJAJAJAJA")
#~ z.putAttr("lo","cualo")
#~ y.insertNode(z)

#~ print x._xmlnode2str()
#~ print colorXML(x,0)

#~ raw = "<iq><item><last>BLABLA</last></item></iq>"
#~ print colorXMLraw(raw)
