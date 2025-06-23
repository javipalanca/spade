
# slixmpp.stringprep
# ~~~~~~~~~~~~~~~~~~~~~~~
# This module is a fallback using python’s stringprep instead of libidn’s.
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2015 Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>
# :license: MIT, see LICENSE for more details
import logging
import stringprep
from slixmpp.util import stringprep_profiles
import encodings.idna

class StringprepError(Exception):
    pass

#: These characters are not allowed to appear in a domain part.
ILLEGAL_CHARS = ('\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r'
                 '\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19'
                 '\x1a\x1b\x1c\x1d\x1e\x1f'
                 ' !"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~\x7f')


# pylint: disable=c0103
#: The nodeprep profile of stringprep used to validate the local,
#: or username, portion of a JID.
_nodeprep = stringprep_profiles.create(
    nfkc=True,
    bidi=True,
    mappings=[
        stringprep_profiles.b1_mapping,
        stringprep.map_table_b2],
    prohibited=[
        stringprep.in_table_c11,
        stringprep.in_table_c12,
        stringprep.in_table_c21,
        stringprep.in_table_c22,
        stringprep.in_table_c3,
        stringprep.in_table_c4,
        stringprep.in_table_c5,
        stringprep.in_table_c6,
        stringprep.in_table_c7,
        stringprep.in_table_c8,
        stringprep.in_table_c9,
        lambda c: c in ' \'"&/:<>@'],
    unassigned=[stringprep.in_table_a1])

def nodeprep(node):
    try:
        return _nodeprep(node)
    except stringprep_profiles.StringPrepError:
        raise StringprepError

# pylint: disable=c0103
#: The resourceprep profile of stringprep, which is used to validate
#: the resource portion of a JID.
_resourceprep = stringprep_profiles.create(
    nfkc=True,
    bidi=True,
    mappings=[stringprep_profiles.b1_mapping],
    prohibited=[
        stringprep.in_table_c12,
        stringprep.in_table_c21,
        stringprep.in_table_c22,
        stringprep.in_table_c3,
        stringprep.in_table_c4,
        stringprep.in_table_c5,
        stringprep.in_table_c6,
        stringprep.in_table_c7,
        stringprep.in_table_c8,
        stringprep.in_table_c9],
    unassigned=[stringprep.in_table_a1])

def resourceprep(resource):
    try:
        return _resourceprep(resource)
    except stringprep_profiles.StringPrepError:
        raise StringprepError

def idna(domain):
    domain_parts = []
    for label in domain.split('.'):
        try:
            label = encodings.idna.nameprep(label)
            encodings.idna.ToASCII(label)
        except UnicodeError:
            raise StringprepError

        if label.startswith('xn--'):
            label = encodings.idna.ToUnicode(label)

        for char in label:
            if char in ILLEGAL_CHARS:
                raise StringprepError

        domain_parts.append(label)
    return '.'.join(domain_parts)

def punycode(domain):
    domain_parts = []
    for label in domain.split('.'):
        try:
            label = encodings.idna.nameprep(label)
            encodings.idna.ToASCII(label)
        except UnicodeError:
            raise StringprepError

        for char in label:
            if char in ILLEGAL_CHARS:
                raise StringprepError

        domain_parts.append(label.encode('ascii'))
    return b'.'.join(domain_parts)

logging.getLogger(__name__).warning('Using slower stringprep, consider '
                                    'using cargo to build the faster version in rust.')
