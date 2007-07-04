#!/usr/bin/python

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("localhost", 2001))
a = s.send('''
(inform
	:sender (agent-identifier
		:name simba-agent
		:addresses
			(sequence
				simba://localhost
			)
		)

	:receiver
		 (set
			(agent-identifier
				:name emissor0@thx1138.dsic.upv.es
				:addresses
					(sequence
						xmpp://emissor0@thx1138.dsic.upv.es
					)
			)
		)

	:content "MECAGOENTUPUTAMADRE"
	:language calo
)
''')
print a
s.close()

