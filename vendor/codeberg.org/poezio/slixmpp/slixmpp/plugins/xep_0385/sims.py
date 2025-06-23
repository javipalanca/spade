import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from slixmpp.plugins import BasePlugin
from slixmpp.stanza import Message
from slixmpp.xmlstream import register_stanza_plugin

from . import stanza

log = logging.getLogger(__name__)


class XEP_0385(BasePlugin):

    """
    XEP-0385: Stateless Inline Media Sharing (SIMS)

    Only support outgoing SIMS, incoming is not handled at all.
    """

    name = "xep_0385"
    description = "XEP-0385: Stateless Inline Media Sharing (SIMS)"
    dependencies = {"xep_0234", "xep_0300", "xep_0372"}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(self.xmpp["xep_0372"].stanza.Reference, stanza.Sims)
        register_stanza_plugin(Message, stanza.Sims)

        register_stanza_plugin(stanza.Sims, stanza.Sources)
        register_stanza_plugin(stanza.Sims, self.xmpp["xep_0234"].stanza.File)
        register_stanza_plugin(stanza.Sources, self.xmpp["xep_0372"].stanza.Reference)

    def get_sims(
        self,
        path: Path,
        uris: Iterable[str],
        media_type: Optional[str],
        desc: Optional[str],
    ):
        sims = stanza.Sims()
        for uri in uris:
            ref = self.xmpp["xep_0372"].stanza.Reference()
            ref["uri"] = uri
            ref["type"] = "data"
            sims["sources"].append(ref)
        if media_type:
            sims["file"]["media-type"] = media_type
        if desc:
            sims["file"]["desc"] = desc
        sims["file"]["name"] = path.name

        stat = path.stat()
        sims["file"]["size"] = stat.st_size
        sims["file"]["date"] = datetime.fromtimestamp(stat.st_mtime)

        h = self.xmpp.plugin["xep_0300"].compute_hash(path)
        h["value"] = h["value"].decode()
        sims["file"].append(h)

        ref = self.xmpp["xep_0372"].stanza.Reference()
        ref.append(sims)
        ref["type"] = "data"
        return ref
