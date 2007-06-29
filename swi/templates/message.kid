<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head><link rel="stylesheet" type="text/css" href="/static/css/webadmin.css"></link>
<title>SPADE Web Administration Tool</title></head>
<body>
<table>
	<tr>
		<td class="cabecera" colspan="2"><h1>SPADE WEB ADMIN</h1></td>
	</tr>
	<tr>
		<td class="lateral">
			<a class="lateral" href="/">Main</a><br/>
			<a class="lateral" href="/pref">Preferences</a><br/>
			<a class="lateral" href="/clients">Agents</a><br/>
			<a class="lateral" href="/services">Services</a><br/>
			<a class="lateral" href="/orgs">Organizations</a><br/>
			<a class="lateral" href="/plugins">Plugins</a>
		</td>
		<td>
			<span class="titulo">Send a message to agent <span py:replace="to">an agent</span></span><br/>
			<table><tr><td>
            	<div>
            	<FORM action="/sendmessage" method="post">
            	<fieldset>
	            <legend>Receivers</legend>
	            <select name="receivers" multiple="multiple" size="${str(len(keys))}">
	            <span py:for="jid in keys">
	            	<span py:if="to==jid">
	            		<option VALUE="${jid}" selected="selected" py:content="jid"></option>
	            	</span>
	            	<span py:if="to!=jid">
	            		<option VALUE="${jid}" py:content="jid"></option>
	            	</span>
	            </span>
	            </select>
	            </fieldset>
	            <fieldset>
	            <legend>Header</legend>
	            <table><tr><td>
	            Performative: <SELECT NAME="performative">
	            <option VALUE="accept-proposal">Accept-Proposal</option>
	            <option VALUE="agree">Agree</option>
	            <option VALUE="cancel">Cancel</option>
	            <option VALUE="cfp">CFP</option>
	            <option VALUE="confirm">Confirm</option>
	            <option VALUE="disconfirm">Disconfirm</option>
	            <option VALUE="failure">Failure</option>
	            <option VALUE="inform">Inform</option>
	            <option VALUE="not-understood">Not-Understood</option>
	            <option VALUE="propagate">Propagate</option>
	            <option VALUE="propose">Propose</option>
	            <option VALUE="proxy">Proxy</option>
	            <option VALUE="query-if">Query-If</option>
	            <option VALUE="query-ref">Query-Ref</option>
	            <option VALUE="refuse">Refuse</option>
	            <option VALUE="reject-proposal">Reject-Proposal</option>
	            <option VALUE="request">Request</option>
	            <option VALUE="request-when">Request-When</option>
	            <option VALUE="request-whenever">Request-Whenever</option>
	            <option VALUE="subscribe">Subscribe</option>
	            </SELECT>
	            </td><td>
	            Sender: <input TYPE="text" NAME="sender"></input>
	            </td><td>
	            Reply To: <input TYPE="text" NAME="reply-to"></input>
	            </td></tr></table>
	            </fieldset>	
	            <fieldset>
	            <legend>Reply Options</legend>
	            <table><tr><td>
	            Reply With: <input TYPE="text" NAME="reply-with"></input>
	            </td><td>
	            Reply By: <input TYPE="text" NAME="reply-by"></input>
	            </td><td>
	            In Reply To: <input TYPE="text" NAME="in-reply-to"></input>
	            </td></tr></table>
	            </fieldset>	
	            <fieldset>
	            <legend>Syntax Options</legend>
	            <table><tr><td>
	            Encoding: <input TYPE="text" NAME="encoding"></input>
	            </td><td>
	            Language: <input TYPE="text" NAME="language"></input>
	            </td><td>
	            Ontology: <input TYPE="text" NAME="ontology"></input>
	            </td></tr></table>
	            </fieldset>	
	            <fieldset>
	            <legend>Conversation Options</legend>
	            <table><tr><td>
	            Protocol: <input TYPE="text" NAME="protocol"></input>
	            </td><td>
	            Conversation ID: <input TYPE="text" NAME="conversation-id"></input>
	            </td></tr></table>
	            </fieldset>	
	            <fieldset>
	            <legend>Content</legend>
	            <table><tr><td>
	            <textarea name="content" rows="10" cols="100"></textarea><BR/>
	            <input TYPE="hidden" NAME="to" VALUE="${to}"></input>
	            <input TYPE="hidden" NAME="fipa" VALUE="YES"></input>
	            </td></tr></table>
	            </fieldset>
	            <input TYPE="submit" VALUE="Send"></input>
	            </FORM>
	            </div>
            </td></tr></table>
        </td>
	</tr>
	<tr>
		<td>#BOTTOM#</td>
	</tr>
</table>

</body>
</html>