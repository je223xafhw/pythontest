var slider = document.getElementById("myRange");
var output = document.getElementById("sval");
var buttonpress = document.getElementById("a_cam");
var getquerybutton = document.getElementById("fetchquerybutton");
var downloadchosen = true;
var downloadcheckbox = document.getElementById("gen");
downloadcheckbox.checked = true;
// output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
// slider.oninput = function () {
//   output.innerHTML = this.value;
// };

getquerybutton.onclick = function () {
  downloadalertdiv = document.getElementById("downloadalert");
  if ((downloadchosen == true) & (downloadalertdiv.style.display === "none")) {
    downloadalertdiv.style.display = "block";
  } else {
    downloadalertdiv.style.display = "none";
  }
};
function enquery() {
  var x = document.getElementById("databasecolumns");
  if ((x.style.display === "none") & (downloadcheckbox.checked == true)) {
    downloadchosen = true;
    x.style.display = "block";
  } else {
    downloadchosen = false;
    x.style.display = "none";
  }
}
