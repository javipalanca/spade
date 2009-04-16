<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'master.kid'">
<head><link rel="stylesheet" type="text/css" href="/static/css/desertsand.css"></link>
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
			<h2>MAIN CONTROL PANEL</h2><br/>
			<table><tr><td>
            	<table class="titulo"><tr><td colspan="2">Server Configuration</td></tr></table>
                <table class="linea"><tr><td>Agent Platform address:</td><td class="der"><span py:replace="servername">#SERVERNAME#</span></td></tr></table>
                <table class="linea"><tr><td>System Platform:</td><td class="der"><span py:replace="platform">#PLATFORM#</span></td></tr></table>
                <table class="linea"><tr><td>Python Version:</td><td class="der"><span py:replace="version">#PYTHONVERSION#</span></td></tr></table>
                <table class="linea"><tr><td>Server Time:</td><td class="der"><span py:replace="time">#TIME#</span></td></tr></table>
                <table class="linea"><tr><td>Restart Platform:</td><td class="der">
                	<form action="/" method="POST"><input type="hidden" name="restart" value="true"></input>
                		<input type="submit" value="Restart"></input></form></td></tr></table>
            </td></tr></table></td>
	</tr>
	<tr>
		<td>#BOTTOM#</td>
	</tr>
</table>

</body>
</html>