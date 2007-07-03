<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'swimaster.kid'">
<head>
	<link rel="stylesheet" type="text/css" href="/static/css/style2.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/lasvegastoo.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/webadmin.css"></link>	
	<link rel="stylesheet" type="text/css" href="/static/css/tform.css"></link>
	<title>SPADE WebAdmin Tool</title>
</head>
<body>
	<div id="content">
		<div id="posts">
			<div class="post">
				<h2 class="title">Send a message to agent <span py:replace="to">an agent</span></h2>
				<div class="meta"></div>
				<div class="story">

		            	<FORM action="/sendmessage" method="post">
							<div id="msgsendup">
				            <input TYPE="submit" VALUE="Send"></input>
							</div>
						<div id="receivers" >
		            	<fieldset class="tform" >
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
						</div>

			            <div id="msgheader" >
						<fieldset class="tform" >
			            <legend>Header</legend>
			            <table class="tform">
							<tr><td>Performative:</td>
								<td><SELECT NAME="performative">
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
						       </td>
							</tr>
							<tr><td>Sender:</td>
								<td><input TYPE="text" NAME="sender" class="txtfield"></input>
			            		</td>
							</tr>
							<tr><td>Reply To:</td>
								<td><input TYPE="text" NAME="reply_to"></input>
			            		</td>
							</tr>
						</table>
			            </fieldset>
						</div>
			
						<div id="replyoptions">
			            <fieldset class="tform" >
			            <legend>Reply Options</legend>
			            <table>
							<tr><td>Reply With:</td>
								<td><input TYPE="text" NAME="reply_with"></input></td>
							</tr>
							<tr><td>Reply By:</td>
								<td><input TYPE="text" NAME="reply_by"></input></td>
							</tr>
							<tr><td>In Reply To</td>
								<td><input TYPE="text" NAME="in_reply_to"></input></td>
			            	</tr>
						</table>
			            </fieldset>	
						</div>
						
						<div id="syntax"  >
			            <fieldset class="tform" >
			            <legend>Syntax Options</legend>
			            <table><tr><td>
			            Encoding:</td><td><input TYPE="text" NAME="encoding"></input>
			            </td></tr><tr><td>
			            Language:</td><td><input TYPE="text" NAME="language"></input>
			            </td></tr><tr><td>
			            Ontology:</td><td><input TYPE="text" NAME="ontology"></input>
			            </td></tr></table>
			            </fieldset>
						</div>
						
						<div id="conversationoptions"  >
			            <fieldset class="tform" >
			            <legend>Conversation Options</legend>
			            <table><tr><td>
			            Protocol:</td><td><input TYPE="text" NAME="protocol"></input>
			            </td></tr><tr><td>
			            Conversation ID:</td><td><input TYPE="text" NAME="conversation_id"></input>
			            </td></tr></table>
			            </fieldset>
						</div>
						
						<div id="msgcontent"  >
			            <fieldset class="tform" >
			            <legend>Content</legend>
			            <table><tr><td>
			            <textarea name="content" rows="10" cols="50"></textarea><BR/>
			            <input TYPE="hidden" NAME="to" VALUE="${to}"></input>
			            <input TYPE="hidden" NAME="fipa" VALUE="YES"></input>
			            </td></tr></table>
			            </fieldset>
						</div>
						<div>&nbsp;</div>
						<div id="msgsend"  >
			            <input TYPE="submit" VALUE="Send"></input>
						</div>
						<div>&nbsp;</div>
			            </FORM>

				</div>
			</div>
		</div>
	</div>	
</body>
</html>