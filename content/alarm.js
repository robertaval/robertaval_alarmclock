/*perform an action when the correct link is clicked. the actions listening for are:
- play
- stop
- update top
- update alarm
- add
- delete
*/

function action (action, ID) {
    var response = "", target = "";
    switch (action) {
        case "play":
            httpGet("alarm/action=play&alarm_id="+ID);
            break;
        case "stop":
            httpGet("alarm/action=stop");
            break;
        case "update_time":
            target = "topbar"
            httpGet("alarm/action=update_time", target);
            break;
        case "update":
            if  (!(document.getElementById(ID+'_editing').checked)) {
            var params = gatherFormData(ID+'_form');
            var name = document.getElementById(ID+'_name').value;
            document.getElementById(ID).setAttribute("id", name);
            target = name;
            httpGet("alarm/" + params, target);
            };
            break;
        case "delete":
            var to_delete = document.getElementById(ID);
            httpGet("alarm/action=delete&alarm_id="+ID);
            to_delete.parentNode.removeChild(to_delete);
            break;
        case "add":
            addWithHttp();
            break;
    };
};

/* parse the alarm form and return an string in
the alarm api format. */
function gatherFormData(formID){
    var i;
    var text = "";
    var params = "action=update"
    var days = ""
    var form = document.getElementById(formID).elements;
    for (i=0; i<form.length; i++){
        var element = form[i];
        text += element.type + " " + element.name + " " +element.value +'<br>'
        switch (element.name) {
            case "alarm_id":
            case "name":
            case "time":
            case "date":
              if (element.value.length >0) {params += '&' + element.name +
                                            '=' + element.value ;};
              break;
            case "repeating":
            case "active":
              params += '&' + element.name + '=' + element.checked.toString();
              break;
            case "day":
              if (element.checked) {days += element.value + ','};
              break;
        };
    };
    if (days.length > 0) {params +='&' + "days="+days};
    return params;
};



function addWithHttp() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "alarm/action=gen_name", true);
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var name = xhttp.responseText;
            var node = document.createElement("div");
            var text = document.createTextNode("new alarm");
            node.setAttribute("id", name);
            node.setAttribute("class", "alarm");
            node.appendChild(text);
            console.log("name generated " + name);
            document.getElementById("alarms_section").appendChild(node);
            httpGet("alarm/action=add&alarm_id="+name, name);};
            };
    xhttp.send();
}

/* perform the actual httpGet request and returns
the response*/
function httpGet(url, target) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, true);
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200 &&  typeof target != 'undefined') {
//            console.log(xhttp.responseText);
            document.getElementById(target).innerHTML = xhttp.responseText;};
        };
    xhttp.send();
}


/* Refresh the topbar every 10 seconds */
window.setInterval(action, 10000, 'update_time');


