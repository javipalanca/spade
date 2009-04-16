<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
	    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
	    <title py:replace="''">Your title goes here</title>
	    <meta py:replace="item[:]"/>
	    <style type="text/css">
	        #pageLogin
	        {
	            font-size: 10px;
	            font-family: verdana;
	            text-align: right;
	        }
	    </style>
	    <style type="text/css" media="screen">
	@import "${tg.url('/static/css/style2.css')}";
	@import "${tg.url('/static/css/lasvegastoo.css')}";
	@import "${tg.url('/static/css/webadmin.css')}";
	@import "${tg.url('/static/css/tform.css')}";
	</style>
</head>
<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
<div py:if="tg.config('identity.on') and not defined('logging_in')" id="pageLogin">
       <span py:if="tg.identity.anonymous">
           <a href="${tg.url('/login')}">Login</a>
       </span>
       <span py:if="not tg.identity.anonymous">
           Welcome ${tg.identity.user.display_name}.
           <a href="${tg.url('/logout')}">Logout</a>
       </span>
</div>

<div id="wrapper">
	<div id="header">
			<h1 class="spadelogo"><a href="/">♠</a></h1>
			<h2 ><a href="/" class="webadmin">WebAdmin Tool</a></h2>
	</div>
	<div id="pages">		
	</div>	

	<div py:replace="[item.text]+item[:]"/>

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