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
Name: {group}\Spade; Filename: {app}\runspade.exe; WorkingDir: {app}
Name: {group}\RMA; Filename: {app}\spade-rma.exe; WorkingDir: {app}
Name: {group}\API Documentation; Filename: {app}\doc\index.html; Tasks: api_install
Name: {group}\Readme; Filename: {app}\readme.txt
Name: {group}\{cm:UninstallProgram, Smart Python multiAgent Development Environment}; Filename: {uninstallexe}
[Files]
Source: dist\doc\epydoc.css; DestDir: {app}\doc; Tasks: api_install
Source: dist\doc\index.html; DestDir: {app}\doc; Tasks: api_install
Source: dist\doc\private\epydoc.css; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\exceptions.Exception-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\frames.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\help.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\index.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\indices.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\Queue.Queue-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.ACLMessage-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.ACLMessage.ACLMessage-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.ACLParser-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.ACLParser.ACLParser-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.AbstractAgent-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.Agent-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.deregisterServiceBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.getPlatformInfoBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.ModifyAgentBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.modifyServiceBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.PlatformAgent-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.registerServiceBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.SearchAgentBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Agent.searchServiceBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AID-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AID.aid-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.AMS-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.AmsAgentDescription-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.DefaultBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.ModifyBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.PlatformBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.RegisterBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.AMS.SearchBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.BasicFipaDateTime.BasicFipaDateTime-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.ACLTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.ANDTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.Behaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.BehaviourTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.FSMBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.MessageTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.NOTTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.OneShotBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.ORTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.PeriodicBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.TimeOutBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Behaviour.XORTemplate-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.DefaultBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.DF-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.DfAgentDescription-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.ModifyBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.RegisterBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.SearchBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.DF.ServiceDescription-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Envelope-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Envelope.Envelope-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.FIPAMessage-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.FIPAMessage.FipaMessage-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.MessageReceiver-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.MessageReceiver.MessageList-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.MessageReceiver.MessageReceiver-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Platform-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Platform.RouteBehaviour-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.Platform.SpadePlatform-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.And-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.CaselessLiteral-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.CharsNotIn-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Combine-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Dict-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Each-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Empty-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.FollowedBy-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Forward-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.GoToColumn-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Group-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Keyword-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.LineEnd-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.LineStart-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Literal-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.MatchFirst-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.NoMatch-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.NotAny-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.OneOrMore-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Optional-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Or-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParseBaseException-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParseElementEnhance-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParseException-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParseExpression-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParseFatalException-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParserElement-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ParseResults-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.PositionToken-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.RecursiveGrammarException-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.SkipTo-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.StringEnd-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.StringStart-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Suppress-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Token-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.TokenConverter-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Upcase-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.White-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.Word-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing.ZeroOrMore-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.pyparsing._ForwardNoRecurse-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.ReceivedObject-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.ReceivedObject.ReceivedObject-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.SL0Parser-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.SL0Parser.SL0Parser-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.spade_backend-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.spade_backend.SpadeBackend-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.XMLCodec-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.XMLCodec.XMLCodec-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.auth-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.auth.Bind-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.auth.NonSASL-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.auth.SASL-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.browser-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.browser.Browser-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.client-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.client.Client-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.client.CommonClient-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.client.Component-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.client.PlugIn-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.commands-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.commands.Commands-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.commands.Command_Handler_Prototype-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.commands.TestCommand-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.debug-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.debug.Debug-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.debug.NoDebug-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.dispatcher.Dispatcher-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.features-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.filetransfer.IBB-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.BadFormat-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.BadNamespacePrefix-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.Conflict-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.ConnectionTimeout-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.DataField-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.DataForm-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.Error-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.ErrorNode-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.HostGone-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.HostUnknown-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.ImproperAddressing-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.InternalServerError-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.InvalidFrom-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.InvalidID-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.InvalidNamespace-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.InvalidXML-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.Iq-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.JID-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.Message-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.NodeProcessed-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.NotAuthorized-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.PolicyViolation-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.Presence-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.Protocol-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.RemoteConnectionFailed-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.ResourceConstraint-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.RestrictedXML-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.SeeOtherHost-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.StreamError-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.SystemShutdown-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.UndefinedCondition-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.UnsupportedEncoding-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.UnsupportedStanzaType-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.UnsupportedVersion-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.protocol.XMLNotWellFormed-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.roster-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.roster.Roster-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.simplexml-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.simplexml.Node-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.simplexml.NodeBuilder-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.simplexml.NT-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.simplexml.T-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.transports-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.transports.error-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.transports.HTTPPROXYsocket-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.transports.TCPsocket-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\spade.xmpp.transports.TLS-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\threading.Thread-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\threading._Verbose-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-everything.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.ACLMessage-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.ACLParser-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.Agent-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.AID-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.AMS-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.Behaviour-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.DF-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.Envelope-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.FIPAMessage-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.MessageReceiver-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.Platform-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.pyparsing-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.ReceivedObject-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.SL0Parser-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.spade_backend-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.XMLCodec-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.auth-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.browser-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.client-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.commands-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.debug-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.features-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.protocol-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.roster-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.simplexml-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc-spade.xmpp.transports-module.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\toc.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\trees.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\xmpp.client.PlugIn-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\_xmlplus.sax.handler.ContentHandler-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\__builtin__.object-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\private\__builtin__.type-class.html; DestDir: {app}\doc\private\; Tasks: api_install
Source: dist\doc\public\epydoc.css; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\exceptions.Exception-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\frames.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\help.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\index.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\indices.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\Queue.Queue-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.ACLMessage-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.ACLMessage.ACLMessage-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.ACLParser-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.ACLParser.ACLParser-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.AbstractAgent-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.Agent-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.deregisterServiceBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.getPlatformInfoBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.ModifyAgentBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.modifyServiceBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.PlatformAgent-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.registerServiceBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.SearchAgentBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Agent.searchServiceBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AID-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AID.aid-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.AMS-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.AmsAgentDescription-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.DefaultBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.ModifyBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.PlatformBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.RegisterBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.AMS.SearchBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.BasicFipaDateTime.BasicFipaDateTime-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.ACLTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.ANDTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.Behaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.BehaviourTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.FSMBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.MessageTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.NOTTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.OneShotBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.ORTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.PeriodicBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.TimeOutBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Behaviour.XORTemplate-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.DefaultBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.DF-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.DfAgentDescription-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.ModifyBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.RegisterBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.SearchBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.DF.ServiceDescription-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Envelope-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Envelope.Envelope-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.FIPAMessage-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.FIPAMessage.FipaMessage-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.MessageReceiver-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.MessageReceiver.MessageList-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.MessageReceiver.MessageReceiver-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Platform-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Platform.RouteBehaviour-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.Platform.SpadePlatform-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.And-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.CaselessLiteral-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.CharsNotIn-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Combine-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Dict-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Each-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Empty-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.FollowedBy-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Forward-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.GoToColumn-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Group-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Keyword-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.LineEnd-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.LineStart-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Literal-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.MatchFirst-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.NoMatch-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.NotAny-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.OneOrMore-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Optional-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Or-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParseBaseException-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParseElementEnhance-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParseException-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParseExpression-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParseFatalException-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParserElement-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ParseResults-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.PositionToken-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.RecursiveGrammarException-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.SkipTo-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.StringEnd-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.StringStart-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Suppress-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Token-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.TokenConverter-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Upcase-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.White-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.Word-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.pyparsing.ZeroOrMore-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.ReceivedObject-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.ReceivedObject.ReceivedObject-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.SL0Parser-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.SL0Parser.SL0Parser-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.spade_backend-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.spade_backend.SpadeBackend-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.XMLCodec-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.XMLCodec.XMLCodec-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.auth-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.auth.Bind-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.auth.NonSASL-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.auth.SASL-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.browser-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.browser.Browser-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.client-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.client.Client-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.client.CommonClient-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.client.Component-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.client.PlugIn-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.commands-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.commands.Commands-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.commands.Command_Handler_Prototype-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.commands.TestCommand-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.debug-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.debug.Debug-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.debug.NoDebug-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.dispatcher.Dispatcher-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.features-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.filetransfer.IBB-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.BadFormat-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.BadNamespacePrefix-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.Conflict-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.ConnectionTimeout-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.DataField-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.DataForm-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.Error-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.ErrorNode-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.HostGone-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.HostUnknown-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.ImproperAddressing-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.InternalServerError-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.InvalidFrom-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.InvalidID-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.InvalidNamespace-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.InvalidXML-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.Iq-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.JID-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.Message-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.NodeProcessed-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.NotAuthorized-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.PolicyViolation-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.Presence-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.Protocol-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.RemoteConnectionFailed-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.ResourceConstraint-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.RestrictedXML-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.SeeOtherHost-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.StreamError-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.SystemShutdown-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.UndefinedCondition-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.UnsupportedEncoding-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.UnsupportedStanzaType-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.UnsupportedVersion-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.protocol.XMLNotWellFormed-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.roster-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.roster.Roster-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.simplexml-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.simplexml.Node-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.simplexml.NodeBuilder-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.simplexml.NT-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.simplexml.T-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.transports-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.transports.error-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.transports.HTTPPROXYsocket-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.transports.TCPsocket-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\spade.xmpp.transports.TLS-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\threading.Thread-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-everything.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.ACLMessage-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.ACLParser-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.Agent-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.AID-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.AMS-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.BasicFipaDateTime-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.Behaviour-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.DF-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.Envelope-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.FIPAMessage-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.MessageReceiver-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.Platform-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.pyparsing-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.ReceivedObject-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.SL0Parser-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.spade_backend-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.XMLCodec-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.auth-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.browser-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.client-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.commands-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.debug-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.dispatcher-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.features-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.filetransfer-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.protocol-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.roster-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.simplexml-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc-spade.xmpp.transports-module.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\toc.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\trees.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\xmpp.client.PlugIn-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\__builtin__.object-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\doc\public\__builtin__.type-class.html; DestDir: {app}\doc\public\; Tasks: api_install
Source: dist\atk.pyd; DestDir: {app}
Source: dist\bz2.pyd; DestDir: {app}
Source: dist\configure.exe; DestDir: {app}
Source: dist\glade.pyd; DestDir: {app}
Source: dist\gobject.pyd; DestDir: {app}
Source: dist\iconv.dll; DestDir: {app}
Source: dist\intl.dll; DestDir: {app}
Source: dist\libatk-1.0-0.dll; DestDir: {app}
Source: dist\libgdk_pixbuf-2.0-0.dll; DestDir: {app}
Source: dist\libgdk-win32-2.0-0.dll; DestDir: {app}
Source: dist\libglade-2.0-0.dll; DestDir: {app}
Source: dist\libglib-2.0-0.dll; DestDir: {app}
Source: dist\libgmodule-2.0-0.dll; DestDir: {app}
Source: dist\libgobject-2.0-0.dll; DestDir: {app}
Source: dist\libgthread-2.0-0.dll; DestDir: {app}
Source: dist\libgtk-win32-2.0-0.dll; DestDir: {app}
Source: dist\libpango-1.0-0.dll; DestDir: {app}
Source: dist\libpangowin32-1.0-0.dll; DestDir: {app}
Source: dist\library.zip; DestDir: {app}
Source: dist\libxml2.dll; DestDir: {app}
Source: dist\MSVCR71.dll; DestDir: {app}
Source: dist\pango.pyd; DestDir: {app}
Source: dist\pyexpat.pyd; DestDir: {app}
Source: dist\python24.dll; DestDir: {app}
Source: dist\readme.txt; DestDir: {app}
Source: dist\runspade.exe; DestDir: {app}
Source: dist\select.pyd; DestDir: {app}
Source: dist\spade-rma.exe; DestDir: {app}
Source: dist\unicodedata.pyd; DestDir: {app}
Source: dist\w9xpopen.exe; DestDir: {app}
Source: dist\zlib1.dll; DestDir: {app}
Source: dist\zlib.pyd; DestDir: {app}
Source: dist\_gtk.pyd; DestDir: {app}
Source: dist\_socket.pyd; DestDir: {app}
Source: dist\_ssl.pyd; DestDir: {app}
Source: spade\xmpp\auth.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\browser.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\client.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\commands.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\debug.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\dispatcher.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\features.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\filetransfer.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\protocol.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\roster.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\simplexml.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\transports.py; DestDir: {app}\src\spade\xmpp
Source: spade\xmpp\__init__.py; DestDir: {app}\src\spade\xmpp
Source: spade\ACLMessage.py; DestDir: {app}\src\spade\
Source: spade\ACLParser.py; DestDir: {app}\src\spade\
Source: spade\Agent.py; DestDir: {app}\src\spade\
Source: spade\AID.py; DestDir: {app}\src\spade\
Source: spade\AMS.py; DestDir: {app}\src\spade\
Source: spade\BasicFipaDateTime.py; DestDir: {app}\src\spade\
Source: spade\Behaviour.py; DestDir: {app}\src\spade\
Source: spade\DF.py; DestDir: {app}\src\spade\
Source: spade\Envelope.py; DestDir: {app}\src\spade\
Source: spade\FIPAMessage.py; DestDir: {app}\src\spade\
Source: spade\MessageReceiver.py; DestDir: {app}\src\spade\
Source: spade\Platform.py; DestDir: {app}\src\spade\
Source: spade\pyparsing.py; DestDir: {app}\src\spade\
Source: spade\ReceivedObject.py; DestDir: {app}\src\spade\
Source: spade\SL0Parser.py; DestDir: {app}\src\spade\
Source: spade\SpadeConfigParser.py; DestDir: {app}\src\spade\
Source: spade\spade_backend.py; DestDir: {app}\src\spade\
Source: spade\XMLCodec.py; DestDir: {app}\src\spade\
Source: spade\__init__.py; DestDir: {app}\src\spade\
Source: runspade.py; DestDir: {app}\src
Source: spade-rma.py; DestDir: {app}\src
Source: configure.py; DestDir: {app}\src
Source: setup.py; DestDir: {app}\src

[Tasks]
Name: api_install; Description: Install API Documentation
Name: lib_install; Description: Install Development Libraries
[Dirs]
Name: {app}\etc
Name: {app}\doc; Tasks: api_install
Name: {app}\doc\private; Tasks: api_install
Name: {app}\doc\public; Tasks: api_install
Name: {app}\usr
Name: {app}\usr\share
Name: {app}\usr\share\spade
Name: {app}\usr\share\spade\jabberd
Name: {app}\usr\share\spade\jabberd\libs
Name: {app}\usr\share\spade\jabberd\spool
Name: {app}\src
Name: {app}\src\spade
Name: {app}\src\spade\xmpp
[Run]
Filename: {app}\configure.exe; WorkingDir: {app}
Filename: python; Parameters: setup.py install_lib; WorkingDir: {app}/src; Tasks: " lib_install"
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
