.. _api-simple-tuto:

Flexible internal API usage
===========================

The :ref:`internal-api` in slixmpp is used to override behavior or simply
to override the default, in-memory storage backend with something persistent.


We will use the XEP-0231 (Bits of Binary) plugin as an example here to show
very basic functionality. Its API reference is in the plugin documentation:
:ref:`api-0231`.

Let us assume we want to keep each bit of binary in a file named with its
content-id, with all metadata.

First, we have to load the plugin:

.. code-block:: python

    from slixmpp import ClientXMPP
    xmpp = ClientXMPP(...)
    xmpp.register_plugin('xep_0231')

This enables the default, in-memory storage.

We have 3 methods to override to provide similar functionality and keep things
coherent.

Here is a class implementing very basic file storage for BoB:

.. code-block:: python

    from slixmpp.plugins.xep_0231 import BitsOfBinary
    from os import makedirs, remove
    from os.path import join, exists
    import base64
    import json

    class BobLoader:
        def __init__(self, directory):
            makedirs(directory, exist_ok=True)
            self.dir = directory

        def set_bob(self, jid=None, node=None, ifrom=None, args=None):
            payload = {
                'data': base64.b64encode(args['data']).decode(),
                'type': args['type'],
                'cid': args['cid'],
                'max_age': args['max_age']
            }
            with open(join(self.dir, args['cid']), 'w') as fd:
                fd.write(json.dumps(payload))

        def get_bob(self, jid=None, node=None, ifrom=None, args=None):
            with open(join(self.dir, args), 'r') as fd:
                payload = json.loads(fd.read())
            bob = BitsOfBinary()
            bob['data'] = base64.b64decode(payload['data'])
            bob['type'] = payload['type']
            bob['max_age'] = payload['max_age']
            bob['cid'] = payload['cid']
            return bob

        def del_bob(self, jid=None, node=None, ifrom=None, args=None):
            path = join(self.dir, args)
            if exists(path):
                remove(path)

Now we need to replace the default handler with ours:

.. code-block:: python


    bobhandler = BobLoader('/tmp/bobcache')
    xmpp.plugin['xep_0231'].api.register(bobhandler.set_bob, 'set_bob')
    xmpp.plugin['xep_0231'].api.register(bobhandler.get_bob, 'get_bob')
    xmpp.plugin['xep_0231'].api.register(bobhandler.del_bob, 'del_bob')


And that’s it, the BoB storage is now made of JSON files living in a
directory (``/tmp/bobcache`` here).


To check that everything works, you can do the following:

.. code-block:: python

    cid = await xmpp.plugin['xep_0231'].set_bob(b'coucou', 'text/plain')
    # A new bob file should appear
    content = await xmpp.plugin['xep_0231'].get_bob(cid=cid)
    assert content['bob']['data'] == b'coucou'

A file should have been created in that directory.
