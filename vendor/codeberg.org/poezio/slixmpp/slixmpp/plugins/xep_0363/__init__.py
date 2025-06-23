# slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Emmanuel Gil Peyrot
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0363.stanza import Request, Slot, Put, Get, Header
from slixmpp.plugins.xep_0363.http_upload import (
    XEP_0363,
    UploadServiceNotFound,
    FileTooBig,
    HTTPError,
    FileUploadError,
)

register_plugin(XEP_0363)
