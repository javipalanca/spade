<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'swimaster.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Services</title>
</head>
<body>
	<div id="content">
		<div id="posts">
			<div class="post">
				<div id="status_block" class="flash" py:if="value_of('tg_flash', None)" py:content="tg_flash"></div>
			</div>
			<div class="post">
				<h2 class="title">Organizations</h2>
				<div class="meta">
				</div>
				<div class="story">
					<table class="clients">
						<tr><th class="b">Name</th><th class="b">Supervisor</th><th class="b">Topology</th><th>Members</th></tr>
						<?python par = "par" ?>
						<span py:for="dad in orgs">
							<tr py:for="serv in dad[0].getServices()">
								<td class="${par}"><span py:replace="serv.getName()">#ORGNAME#</span></td>
		                		<td class="${par}"><a href="/message/${str(dad[0].getAID().getName())}" py:content="str(dad[0].getAID().getName())">AID</a></td>
								<td class="${par}"><span py:replace="serv.getProperty('topology')">#TOPOLOGY#</span></td>
								<td class="${par}"><span py:replace="str(dad[1])">#MEMBERS#</span></td>
								<?python
								if par=="par":
									par="impar"
								else:
									par="par" ?>
		                	</tr>
						</span>
		            </table>
				</div>
			</div>
		</div>
	</div>
</body>
</html>