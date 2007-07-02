<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
	<link rel="stylesheet" type="text/css" href="/static/css/lasvegastoo.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/webadmin.css"></link>
	<link rel="stylesheet" type="text/css" href="/static/css/tform.css"></link>
	<title>SPADE WebAdmin Tool</title>
</head>
<body>
<div id="wrapper">
	<div id="header">
			<h1><a href="#">SPADE</a></h1>
			<h2><a href="#">WebAdmin Tool</a></h2>
	</div>
	<div id="pages">
	</div>
	<div id="content">
		<div id="posts">
			<div class="post">
				<div id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash"></div>
				<h2 class="title">Agent List</h2>
				<div class="meta">
				</div>
				<div class="story">
					<table class="linea">
						<tr><th class="b">AID</th><th class="b">Ownership</th><th class="b">State</th></tr>
						<?python par = "par" ?>
						<tr py:for="agent,v in agents.items()">
		                	<td class="${par}"><a href="/message/${str(agent)}" py:content="str(agent)">AID</a></td><td class="${par}"><span py:replace="v.getOwnership()">#OWNERSHIP#</span></td><td class="${par}"><span py:replace="v.getState()">#STATE#</span></td>
		<?python
		if par=="par":
			par="impar"
		else:
			par="par" ?>
		                </tr>
		            </table>
				</div>
			</div>
		</div>
	</div>
	<div id="sidebarmenu" class="boxed">
		<h2 class="heading">Menu</h2>
		<div class="content">
			<ul>
				<li class="first"><a href="/">Main</a></li>
				<li><a href="/pref">Preferences</a></li>
				<li><a href="/clients">Agents</a></li>
				<li><a href="/services">Services</a></li>
				<li><a href="/orgs">Organizations</a></li>
				<li><a href="/plugins">Plugins</a></li>
			</ul>
		</div>
	</div>
</div>
</body>
</html>