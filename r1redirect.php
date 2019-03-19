<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<?php

	//
	// URL of R1Soft SBM (NOTE: Use HTTPS to prevent transmission of clear text)
	// Example: https://127.0.0.1
	//
	$SBM_URL = "<URL>";

	//
	// ID of the Control Panel
	// Example: c1568882-3597-4931-84bb-d591eceb63f8
	//
	$CONTROL_PANEL_ID = "<ID>";

?>
<html>
	<head>
		<title>
			Redirecting to R1Soft SBM
		</title>
	</head>
	<body onLoad="javascript:document.f.submit()">
		<br>
		<br>
		<center>
			Redirecting to R1Soft SBM, please wait..
		</center>
		<form name=f method="POST" action="<?php echo $SBM_URL ?>/j_spring_security_check">
			<input name=cpID type=hidden value="<?php echo $CONTROL_PANEL_ID ?>">
			<input name=j_username type=hidden value="<?php echo $_ENV['REMOTE_USER'] ?>">
			<input name=j_password type=hidden value="<?php echo $_ENV['REMOTE_PASSWORD'] ?>">
		</form>
	</body>
</html>
