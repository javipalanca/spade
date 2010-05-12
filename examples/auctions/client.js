var xmlHttp

function showHint()
{
str="0";

/*if (str.length==0)
  {
  document.getElementById("txtHint").innerHTML="";
  return;
  }
*/

xmlHttp=GetXmlHttpObject()
if (xmlHttp==null)
  {
  alert ("Your browser does not support AJAX!");
  return;
  }
var url="getauctiondata";
url=url+"?q="+str;
url=url+"&sid="+Math.random();
xmlHttp.onreadystatechange=stateChanged;
xmlHttp.open("GET",url,true);
xmlHttp.send(null);
str = str + str;
setTimeout("showHint()",500);
}

function auction_update()
{
	xmlHttp=GetXmlHttpObject()
	if (xmlHttp==null)
  	{
  		alert ("Your browser does not support AJAX!");
  		return;
  	}

	var url="getauctiondata";
	//url=url+"?key="+key;
	//url=url+"&sid="+Math.random();
	xmlHttp.onreadystatechange=stateChanged;
	xmlHttp.open("GET",url,true);
	xmlHttp.send(null);
	setTimeout("auction_update()",1000);
}

function stateChanged()
{
	if (xmlHttp.readyState==4)
	{
		// Get data
		var resp = xmlHttp.responseText.split(";;");
		for (i in resp)
		{
			if (resp[i].length!=0) {
				var r = resp[i].split(" ");
				// Process data
				time_id = "time_" + r[0];
				price_id = "price_" + r[0];
				winner_id = "winner_" + r[0];

				time_str = r[1];
				price_str = r[2];
				winner_str = r[3];

				/*
				# Build time left
#				time_left = int(auction["time"])
#				days_left = int(time_left / 86400)
#				time_left = time_left - (86400*days_left)
#				hours_left = int(time_left / 3600)
#				time_left = time_left - (3600*hours_left)
#				minutes_left = int(time_left / 60)
#				time_left = time_left - (60*minutes_left)
#				seconds_left = time_left % 60
				*/

				var time_left = parseInt(time_str);
				var days_left = parseInt(time_left / 86400);
				time_left = time_left - (86400*days_left);
				var hours_left = parseInt(time_left / 3600);
				time_left = time_left - (3600*hours_left);
				var minutes_left = parseInt(time_left / 60);
				time_left = time_left - (60*minutes_left);
				var seconds_left = time_left % 60;

				var formatted_time = "";
				formatted_time = formatted_time + days_left + "d ";
				formatted_time = formatted_time + hours_left + "h ";
				formatted_time = formatted_time + minutes_left + "m ";
				formatted_time = formatted_time + seconds_left + "s";

				document.getElementById( time_id).innerHTML = formatted_time;
				document.getElementById( price_id).innerHTML = price_str;
				document.getElementById( winner_id).innerHTML = winner_str;
			}
		}

		//document.getElementById("txtHint").innerHTML=xmlHttp.responseText;
	}
}

function GetXmlHttpObject()
{
var xmlHttp=null;
try
  {
  // Firefox, Opera 8.0+, Safari
  xmlHttp=new XMLHttpRequest();
  }
catch (e)
  {
  // Internet Explorer
  try
    {
    xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
    }
  catch (e)
    {
    xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
  }
return xmlHttp;
}

