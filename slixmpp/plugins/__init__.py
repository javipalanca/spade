# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import PluginManager, PluginNotFound, BasePlugin
from slixmpp.plugins.base import register_plugin, load_plugin


PLUGINS = [
    # XEPS
    'xep_0004',  # Data Forms
    'xep_0009',  # Jabber-RPC
    'xep_0012',  # Last Activity
    'xep_0013',  # Flexible Offline Message Retrieval
#   'xep_0016',  # Privacy Lists. Don’t automatically load
    'xep_0020',  # Feature Negotiation
    'xep_0027',  # Current Jabber OpenPGP Usage
    'xep_0030',  # Service Discovery
    'xep_0033',  # Extended Stanza Addresses
    'xep_0045',  # Multi-User Chat (Client)
    'xep_0047',  # In-Band Bytestreams
#   'xep_0048',  # Legacy Bookmarks. Don’t automatically load
    'xep_0049',  # Private XML Storage
    'xep_0050',  # Ad-hoc Commands
    'xep_0054',  # vcard-temp
    'xep_0055',  # Jabber Search
    'xep_0059',  # Result Set Management
    'xep_0060',  # Pubsub (Client)
    'xep_0065',  # SOCKS5 Bytestreams
    'xep_0066',  # Out of Band Data
    'xep_0070',  # Verifying HTTP Requests via XMPP
    'xep_0071',  # XHTML-IM
    'xep_0077',  # In-Band Registration
#   'xep_0078',  # Non-SASL auth. Don’t automatically load
    'xep_0079',  # Advanced Message Processing
    'xep_0080',  # User Location
    'xep_0082',  # XMPP Date and Time Profiles
    'xep_0084',  # User Avatar
    'xep_0085',  # Chat State Notifications
    'xep_0086',  # Legacy Error Codes
#   'xep_0091',  # Legacy Delayed Delivery. Don’t automatically load
    'xep_0092',  # Software Version
#   'xep_0095',  # Legacy Stream Initiation. Don’t automatically load
#   'xep_0096',  # Legacy SI File Transfer. Don’t automatically load
    'xep_0100',  # Gateway interaction
    'xep_0106',  # JID Escaping
    'xep_0107',  # User Mood
    'xep_0108',  # User Activity
    'xep_0115',  # Entity Capabilities
    'xep_0118',  # User Tune
    'xep_0122',  # Data Forms Validation
    'xep_0128',  # Extended Service Discovery
    'xep_0131',  # Standard Headers and Internet Metadata
    'xep_0133',  # Service Administration
    'xep_0152',  # Reachability Addresses
    'xep_0153',  # vCard-Based Avatars
    'xep_0163',  # Personal Eventing Protocol
    'xep_0172',  # User Nickname
    'xep_0184',  # Message Receipts
    'xep_0186',  # Invisible Command
    'xep_0191',  # Blocking Command
    'xep_0196',  # User Gaming
    'xep_0198',  # Stream Management
    'xep_0199',  # Ping
    'xep_0202',  # Entity Time
    'xep_0203',  # Delayed Delivery
    'xep_0221',  # Data Forms Media Element
    'xep_0222',  # Persistent Storage of Public Data via Pubsub
    'xep_0223',  # Persistent Storage of Private Data via Pubsub
    'xep_0224',  # Attention
    'xep_0231',  # Bits of Binary
    'xep_0235',  # OAuth Over XMPP
#   'xep_0242',  # XMPP Client Compliance 2009. Don’t automatically load
    'xep_0249',  # Direct MUC Invitations
    'xep_0256',  # Last Activity in Presence
    'xep_0257',  # Client Certificate Management for SASL EXTERNAL
    'xep_0258',  # Security Labels in XMPP
    'xep_0264',  # Jingle Content Thumbnails
#   'xep_0270',  # XMPP Compliance Suites 2010. Don’t automatically load
    'xep_0279',  # Server IP Check
    'xep_0280',  # Message Carbons
    'xep_0292',  # vCard4 Over XMPP
    'xep_0297',  # Stanza Forwarding
    'xep_0300',  # Use of Cryptographic Hash Functions in XMPP
#   'xep_0302',  # XMPP Compliance Suites 2012. Don’t automatically load
    'xep_0308',  # Last Message Correction
    'xep_0313',  # Message Archive Management
    'xep_0317',  # Hats
    'xep_0319',  # Last User Interaction in Presence
#   'xep_0323',  # IoT Systems Sensor Data. Don’t automatically load
#   'xep_0325',  # IoT Systems Control. Don’t automatically load
    'xep_0332',  # HTTP Over XMPP Transport
    'xep_0333',  # Chat Markers
    'xep_0334',  # Message Processing Hints
    'xep_0335',  # JSON Containers
    'xep_0352',  # Client State Indication
    'xep_0353',  # Jingle Message Initiation
    'xep_0356',  # Privileged entity
    'xep_0359',  # Unique and Stable Stanza IDs
    'xep_0363',  # HTTP File Upload
    'xep_0369',  # MIX-CORE
    'xep_0377',  # Spam reporting
    'xep_0380',  # Explicit Message Encryption
    'xep_0382',  # Spoiler Messages
    'xep_0385',  # Stateless Inline Media Sharing (SIMS)
    'xep_0394',  # Message Markup
    'xep_0402',  # PEP Native Bookmarks
    'xep_0403',  # MIX-Presence
    'xep_0404',  # MIX-Anon
    'xep_0405',  # MIX-PAM
    'xep_0410',  # MUC Self-ping
    'xep_0421',  # Anonymous unique occupant identifiers for MUCs
    'xep_0422',  # Message Fastening
    'xep_0424',  # Message Retraction
    'xep_0425',  # Moderated Message Retraction
    'xep_0428',  # Message Fallback
    'xep_0437',  # Room Activity Indicators
    'xep_0439',  # Quick Response
    'xep_0441',  # Message Archive Management Preferences
    'xep_0444',  # Message Reactions
    'xep_0446',  # File metadata element
    'xep_0447',  # Stateless file sharing
    'xep_0461',  # Message Replies
    'xep_0469',  # Bookmarks Pinning
    'xep_0482',  # Call Invites
    'xep_0490',  # Message Displayed Synchronization
    'xep_0492',  # Chat Notification Settings
    # Meant to be imported by plugins
]

__all__ = PLUGINS + [
    'PluginManager',
    'PluginNotFound',
    'BasePlugin',
    'register_plugin',
    'load_plugin',
]
