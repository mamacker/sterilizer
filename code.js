let light_status = true;
function loadDoc(loc, cb) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (cb) {
        cb(JSON.parse(this.responseText));
      }
    }
  };
  xhttp.open("GET", loc, true);
  xhttp.send();
}

document.getElementById("on").addEventListener("click", () => {
  loadDoc("/on");
});

document.getElementById("status").addEventListener("click", () => {
  if (light_status) {
    loadDoc("/off");
  }
});

document.getElementById("off").addEventListener("click", () => {
  loadDoc("/off");
});

function set_status(val) {
  if (val) {
    document.getElementById("status").innerHTML = "&#x1f4a1;"
  } else {
    document.getElementById("status").innerHTML = "OFF"
  }
}

setInterval(() => {
  loadDoc("/status", (current) => {
    if (current && current.ison) {
      set_status(current.ison);
    } else {
      set_status(false);
    }
  });
}, 500);
