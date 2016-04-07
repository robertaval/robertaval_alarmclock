<!DOCTYPE html>
<html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <link rel="stylesheet" type="text/css" href="style.css">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css">
      <title>alarm</title>
    </head>

<body>
  <div id="container">
      {{!topbar}}
    <div id="alarms_section">
       {{!alarms}}
    </div>
    <div id="addbar">
     <div class="button_add">
       <a href="#" onclick="action('add')">+</a>
     </div>
    </div>
  </div>

<script src="alarm.js"></script>
</body>
</html>
