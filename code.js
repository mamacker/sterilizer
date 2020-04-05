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
    document.getElementById("status").innerHTML = "ON"
  } else {
    document.getElementById("status").innerHTML = "OFF"
  }
}

function set_safety(val) {
  switch(val) {
    case "open":
      document.getElementById("safety").innerHTML = "Lid Open"
      break;
    case "":
      document.getElementById("safety").innerHTML = "Safe"
      break;
  }
}

setInterval(() => {
  loadDoc("/status", (current) => {
    if (current && current.ison) {
      set_status(current.ison);
    } else {
      set_status(false);
    }

    if (current && current.safety_state !== undefined) {
      set_safety(current.safety_state);
    }
  });
}, 500);
