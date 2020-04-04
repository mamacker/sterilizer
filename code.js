function loadDoc(loc) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
     alert(this.responseText);
    }
  };
  xhttp.open("GET", loc, true);
  xhttp.send();
}

document.getElementById("on").addEventListener("click", () => {
  loadDoc("/on");
});

document.getElementById("off").addEventListener("click", () => {
  loadDoc("/off");
});
