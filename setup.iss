[Setup]
VersionInfoVersion=1.9.3
VersionInfoCompany=Grupo de Tecnología Informática-Inteligencia Artificial, DSIC.
VersionInfoDescription=Smart Python multiAgent Development Environment
VersionInfoTextVersion=SPADE 1.9.3
VersionInfoCopyright=Copyright Grupo de Tecnología Informática-Inteligencia Artificial
AppName=Smart Python multiAgent Development Environment
AppVerName=SPADE 1.9.3
DefaultDirName={pf}\Spade
AppCopyright=Copyright Grupo de Tecnología Informática-Inteligencia Artificial
DefaultGroupName=Spade
ShowLanguageDialog=yes

[Icons]
Name: {group}\Spade; Filename: {app}\runspade.py; WorkingDir: {app}
Name: {group}\RMA; Filename: {app}\spade-rma.py; WorkingDir: {app}
Name: {group}\API Documentation; Filename: {app}\doc\index.html; Tasks: api_install
Name: {group}\Readme; Filename: {app}\readme.txt
Name: {group}\{cm:UninstallProgram, Smart Python multiAgent Development Environment}; Filename: {uninstallexe}

[Tasks]
Name: api_install; Description: Install API Documentation
Name: lib_install; Description: Install Development Libraries

[Run]
Filename: python; WorkingDir: {app}; Parameters: configure.py
Filename: python; Parameters: setup.py install_lib; WorkingDir: {app}; Tasks: " lib_install"

[Files]
Source: setup.py; DestDir: {app}
Source: runspade.py; DestDir: {app}
Source: spade-rma.py; DestDir: {app}
Source: configure.py; DestDir: {app}
Source: spade\__init__.py; DestDir: {app}\spade
Source: spade\ACLMessage.py; DestDir: {app}\spade
Source: spade\ACLParser.py; DestDir: {app}\spade
Source: spade\Agent.py; DestDir: {app}\spade
Source: spade\AID.py; DestDir: {app}\spade
Source: spade\AMS.py; DestDir: {app}\spade
Source: spade\BasicFipaDateTime.py; DestDir: {app}\spade
Source: spade\Behaviour.py; DestDir: {app}\spade
Source: spade\DF.py; DestDir: {app}\spade
Source: spade\Envelope.py; DestDir: {app}\spade
Source: spade\FIPAMessage.py; DestDir: {app}\spade
Source: spade\MessageReceiver.py; DestDir: {app}\spade
Source: spade\Platform.py; DestDir: {app}\spade
Source: spade\pyparsing.py; DestDir: {app}\spade
Source: spade\ReceivedObject.py; DestDir: {app}\spade
Source: spade\SL0Parser.py; DestDir: {app}\spade
Source: spade\spade_backend.py; DestDir: {app}\spade
Source: spade\SpadeConfigParser.py; DestDir: {app}\spade
Source: spade\XMLCodec.py; DestDir: {app}\spade
Source: spade\xmpp\__init__.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\auth.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\browser.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\client.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\commands.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\debug.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\dispatcher.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\features.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\filetransfer.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\protocol.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\roster.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\simplexml.py; DestDir: {app}\spade\xmpp
Source: spade\xmpp\transports.py; DestDir: {app}\spade\xmpp
Source: usr\share\spade\rma.glade; DestDir: {app}\usr\share\spade
Source: usr\share\spade\jabberd\jabberd.exe; DestDir: {app}\usr\share\spade\jabberd
Source: usr\share\spade\jabberd\libs\dnsrv.dll; DestDir: {app}\usr\share\spade\jabberd\libs
Source: usr\share\spade\jabberd\libs\jsm.dll; DestDir: {app}\usr\share\spade\jabberd\libs
Source: usr\share\spade\jabberd\libs\pthsock_client.dll; DestDir: {app}\usr\share\spade\jabberd\libs
Source: usr\share\spade\jabberd\libs\xdb_file.dll; DestDir: {app}\usr\share\spade\jabberd\libs
Source: usr\share\spade\jabberd\libs\dialback.dll; DestDir: {app}\usr\share\spade\jabberd\libs
Source: doc\api\index.html; DestDir: {app}\doc
Source: doc\api\epydoc.css; DestDir: {app}\doc
Source: doc\api\public\__builtin__.object-class.html; DestDir: {app}\doc\public
Source: doc\api\public\__builtin__.type-class.html; DestDir: {app}\doc\public
Source: doc\api\public\epydoc.css; DestDir: {app}\doc\public
Source: doc\api\public\exceptions.Exception-class.html; DestDir: {app}\doc\public
Source: doc\api\public\frames.html; DestDir: {app}\doc\public
Source: doc\api\public\help.html; DestDir: {app}\doc\public
Source: doc\api\public\index.html; DestDir: {app}\doc\public
Source: doc\api\public\indices.html; DestDir: {app}\doc\public
Source: doc\api\public\Queue.Queue-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.ACLMessage.ACLMessage-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.ACLMessage-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.ACLParser.ACLParser-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.ACLParser-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.AbstractAgent-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.Agent-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.deregisterServiceBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.getPlatformInfoBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.ModifyAgentBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.modifyServiceBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.PlatformAgent-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.registerServiceBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.SearchAgentBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent.searchServiceBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Agent-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AID.aid-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AID-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.AmsAgentDescription-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.AMS-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.DefaultBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.ModifyBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.PlatformBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.RegisterBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS.SearchBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.AMS-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.BasicFipaDateTime.BasicFipaDateTime-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.ACLTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.ANDTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.Behaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.BehaviourTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.FSMBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.MessageTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.NOTTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.OneShotBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.ORTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.PeriodicBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.TimeOutBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour.XORTemplate-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Behaviour-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.DefaultBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.DfAgentDescription-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.DF-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.ModifyBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.RegisterBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.SearchBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF.ServiceDescription-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.DF-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Envelope.Envelope-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Envelope-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.FIPAMessage.FipaMessage-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.FIPAMessage-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.MessageReceiver.MessageList-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.MessageReceiver.MessageReceiver-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.MessageReceiver-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Platform.RouteBehaviour-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Platform.SpadePlatform-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.Platform-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.And-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.CaselessLiteral-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.CharsNotIn-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Combine-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Dict-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Each-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Empty-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.FollowedBy-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Forward-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.GoToColumn-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Group-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Keyword-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.LineEnd-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.LineStart-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Literal-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.MatchFirst-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.NoMatch-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.NotAny-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.OneOrMore-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Optional-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Or-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParseBaseException-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParseElementEnhance-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParseException-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParseExpression-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParseFatalException-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParserElement-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ParseResults-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.PositionToken-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.RecursiveGrammarException-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.SkipTo-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.StringEnd-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.StringStart-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Suppress-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Token-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.TokenConverter-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Upcase-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.White-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.Word-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing.ZeroOrMore-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.pyparsing-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.ReceivedObject.ReceivedObject-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.ReceivedObject-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.SL0Parser.SL0Parser-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.SL0Parser-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.spade_backend.SpadeBackend-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.spade_backend-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.XMLCodec.XMLCodec-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.XMLCodec-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.auth.Bind-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.auth.NonSASL-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.auth.SASL-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.auth-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.browser.Browser-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.browser-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.client.Client-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.client.CommonClient-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.client.Component-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.client.PlugIn-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.client-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.commands.Command_Handler_Prototype-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.commands.Commands-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.commands.TestCommand-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.commands-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.debug.Debug-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.debug.NoDebug-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.debug-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.dispatcher.Dispatcher-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.features-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.filetransfer.IBB-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.BadFormat-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.BadNamespacePrefix-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.Conflict-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.ConnectionTimeout-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.DataField-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.DataForm-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.Error-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.ErrorNode-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.HostGone-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.HostUnknown-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.ImproperAddressing-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.InternalServerError-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.InvalidFrom-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.InvalidID-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.InvalidNamespace-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.InvalidXML-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.Iq-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.JID-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.Message-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.NodeProcessed-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.NotAuthorized-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.PolicyViolation-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.Presence-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.Protocol-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.RemoteConnectionFailed-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.ResourceConstraint-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.RestrictedXML-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.SeeOtherHost-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.StreamError-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.SystemShutdown-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.UndefinedCondition-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.UnsupportedEncoding-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.UnsupportedStanzaType-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.UnsupportedVersion-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol.XMLNotWellFormed-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.protocol-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.roster.Roster-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.roster-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.simplexml.NodeBuilder-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.simplexml.Node-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.simplexml.NT-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.simplexml.T-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.simplexml-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.transports.error-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.transports.HTTPPROXYsocket-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.transports.TCPsocket-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.transports.TLS-class.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp.transports-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade.xmpp-module.html; DestDir: {app}\doc\public
Source: doc\api\public\spade-module.html; DestDir: {app}\doc\public
Source: doc\api\public\threading.Thread-class.html; DestDir: {app}\doc\public
Source: doc\api\public\toc.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-everything.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.ACLMessage-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.ACLParser-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.Agent-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.AID-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.AMS-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.Behaviour-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.DF-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.Envelope-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.FIPAMessage-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.MessageReceiver-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.Platform-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.pyparsing-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.ReceivedObject-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.SL0Parser-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.spade_backend-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.XMLCodec-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.auth-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.browser-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.client-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.commands-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.debug-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.features-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.protocol-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.roster-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.simplexml-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp.transports-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade.xmpp-module.html; DestDir: {app}\doc\public
Source: doc\api\public\toc-spade-module.html; DestDir: {app}\doc\public
Source: doc\api\public\trees.html; DestDir: {app}\doc\public
Source: doc\api\public\xmpp.client.PlugIn-class.html; DestDir: {app}\doc\public
Source: doc\api\private\__builtin__.object-class.html; DestDir: {app}\doc\private
Source: doc\api\private\__builtin__.type-class.html; DestDir: {app}\doc\private
Source: doc\api\private\_xmlplus.sax.handler.ContentHandler-class.html; DestDir: {app}\doc\private
Source: doc\api\private\epydoc.css; DestDir: {app}\doc\private
Source: doc\api\private\exceptions.Exception-class.html; DestDir: {app}\doc\private
Source: doc\api\private\frames.html; DestDir: {app}\doc\private
Source: doc\api\private\help.html; DestDir: {app}\doc\private
Source: doc\api\private\index.html; DestDir: {app}\doc\private
Source: doc\api\private\indices.html; DestDir: {app}\doc\private
Source: doc\api\private\Queue.Queue-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.ACLMessage.ACLMessage-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.ACLMessage-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.ACLParser.ACLParser-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.ACLParser-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.AbstractAgent-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.Agent-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.deregisterServiceBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.getPlatformInfoBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.ModifyAgentBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.modifyServiceBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.PlatformAgent-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.registerServiceBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.SearchAgentBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent.searchServiceBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Agent-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AID.aid-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AID-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.AmsAgentDescription-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.AMS-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.DefaultBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.ModifyBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.PlatformBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.RegisterBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS.SearchBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.AMS-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.BasicFipaDateTime.BasicFipaDateTime-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.ACLTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.ANDTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.Behaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.BehaviourTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.FSMBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.MessageTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.NOTTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.OneShotBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.ORTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.PeriodicBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.TimeOutBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour.XORTemplate-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Behaviour-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.DefaultBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.DfAgentDescription-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.DF-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.ModifyBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.RegisterBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.SearchBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF.ServiceDescription-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.DF-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Envelope.Envelope-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Envelope-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.FIPAMessage.FipaMessage-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.FIPAMessage-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.MessageReceiver.MessageList-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.MessageReceiver.MessageReceiver-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.MessageReceiver-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Platform.RouteBehaviour-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Platform.SpadePlatform-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.Platform-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing._ForwardNoRecurse-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.And-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.CaselessLiteral-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.CharsNotIn-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Combine-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Dict-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Each-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Empty-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.FollowedBy-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Forward-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.GoToColumn-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Group-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Keyword-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.LineEnd-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.LineStart-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Literal-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.MatchFirst-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.NoMatch-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.NotAny-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.OneOrMore-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Optional-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Or-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParseBaseException-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParseElementEnhance-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParseException-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParseExpression-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParseFatalException-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParserElement-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ParseResults-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.PositionToken-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.RecursiveGrammarException-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.SkipTo-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.StringEnd-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.StringStart-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Suppress-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Token-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.TokenConverter-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Upcase-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.White-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.Word-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing.ZeroOrMore-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.pyparsing-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.ReceivedObject.ReceivedObject-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.ReceivedObject-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.SL0Parser.SL0Parser-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.SL0Parser-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.spade_backend.SpadeBackend-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.spade_backend-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.XMLCodec.XMLCodec-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.XMLCodec-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.auth.Bind-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.auth.NonSASL-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.auth.SASL-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.auth-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.browser.Browser-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.browser-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.client.Client-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.client.CommonClient-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.client.Component-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.client.PlugIn-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.client-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.commands.Command_Handler_Prototype-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.commands.Commands-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.commands.TestCommand-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.commands-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.debug.Debug-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.debug.NoDebug-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.debug-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.dispatcher.Dispatcher-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.features-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.filetransfer.IBB-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.BadFormat-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.BadNamespacePrefix-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.Conflict-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.ConnectionTimeout-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.DataField-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.DataForm-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.Error-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.ErrorNode-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.HostGone-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.HostUnknown-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.ImproperAddressing-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.InternalServerError-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.InvalidFrom-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.InvalidID-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.InvalidNamespace-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.InvalidXML-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.Iq-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.JID-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.Message-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.NodeProcessed-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.NotAuthorized-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.PolicyViolation-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.Presence-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.Protocol-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.RemoteConnectionFailed-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.ResourceConstraint-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.RestrictedXML-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.SeeOtherHost-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.StreamError-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.SystemShutdown-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.UndefinedCondition-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.UnsupportedEncoding-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.UnsupportedStanzaType-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.UnsupportedVersion-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol.XMLNotWellFormed-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.protocol-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.roster.Roster-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.roster-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.simplexml.NodeBuilder-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.simplexml.Node-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.simplexml.NT-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.simplexml.T-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.simplexml-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.transports.error-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.transports.HTTPPROXYsocket-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.transports.TCPsocket-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.transports.TLS-class.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp.transports-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade.xmpp-module.html; DestDir: {app}\doc\private
Source: doc\api\private\spade-module.html; DestDir: {app}\doc\private
Source: doc\api\private\threading._Verbose-class.html; DestDir: {app}\doc\private
Source: doc\api\private\threading.Thread-class.html; DestDir: {app}\doc\private
Source: doc\api\private\toc.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-everything.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.ACLMessage-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.ACLParser-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.Agent-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.AID-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.AMS-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.Behaviour-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.DF-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.Envelope-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.FIPAMessage-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.MessageReceiver-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.Platform-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.pyparsing-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.ReceivedObject-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.SL0Parser-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.spade_backend-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.XMLCodec-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.auth-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.browser-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.client-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.commands-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.debug-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.features-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.protocol-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.roster-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.simplexml-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp.transports-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade.xmpp-module.html; DestDir: {app}\doc\private
Source: doc\api\private\toc-spade-module.html; DestDir: {app}\doc\private
Source: doc\api\private\trees.html; DestDir: {app}\doc\private
Source: doc\api\private\xmpp.client.PlugIn-class.html; DestDir: {app}\doc\private
Source: readme.txt; DestDir: {app}; Flags: isreadme
[Dirs]
Name: {app}\spade
Name: {app}\spade\xmpp
Name: {app}\etc
Name: {app}\usr
Name: {app}\usr\share
Name: {app}\usr\share\spade
Name: {app}\usr\share\spade\jabberd
Name: {app}\usr\share\spade\jabberd\libs
Name: {app}\usr\share\spade\jabberd\spool
Name: {app}\doc
Name: {app}\doc\public
Name: {app}\doc\private

[Code]
{
var
  UserPage: TInputQueryWizardPage;


procedure InitializeWizard;
begin
  UserPage := CreateInputQueryPage(wpWelcome,
    'Compuetr Name', '',
    'Please specify the computer name, then click Next.');
  UserPage.Add('Computer Name:', False);

  // Set default values, using settings that were stored last time if possible
  UserPage.Values[0] := 'localhost';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  // Validate certain pages before allowing the user to proceed
  if CurPageID = UserPage.ID then begin
    if UserPage.Values[0] = '' then begin
      MsgBox('You must enter the computer name.', mbError, MB_OK);
      Result := False;
    end;
  end
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  case CurPageID of
    wpFinished:
      MsgBox('CurPageChanged:' #13#13 'Welcome to final page of this demo. Click Finish to exit.', mbInformation, MB_OK);
  end;
end;
}
[UninstallDelete]
Name: {app}; Type: filesandordirs; Tasks: 
