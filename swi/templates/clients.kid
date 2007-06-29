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
			<span class="titulo">AGENT LIST</span><br/>
			<table>
				<tr><td class="b">AID</td><td class="b">Ownership</td><td class="b">State</td></tr>
				<?python par = "par" ?>
				<tr py:for="agent,v in agents.items()">
                	<td class="${par}"><span py:replace="str(agent)">AID</span></td><td class="${par}"><span py:replace="v.getOwnership()">#OWNERSHIP#</span></td><td class="${par}"><span py:replace="v.getState()">#STATE#</span></td>
<?python
if par=="par":
	par="impar"
else:
	par="par" ?>
                </tr>
            </table></td>
	</tr>
	<tr>
		<td>#BOTTOM#</td>
	</tr>
</table>

</body>
</html>