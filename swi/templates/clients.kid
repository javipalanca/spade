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
				<div id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash"></div>
				<h2 class="title">Agent List</h2>
				<div class="meta">
				</div>
				<div class="story">
					<table class="clients">
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
</body>
</html>