async function fileselhandler() {
    let a = await eel.fileinihandle("foldid")()
    .then(a => {
        handledata(a);
    })
    .catch(e => console.log(e));
}
function handledata(data) {
    for (elem of data) {
        //var colormatch = {"foldid":"#000000", "docid":"#ffbb00", "imgid":"#052f9c", "vidid":"#a80032", "audid"::"#4300a8", "othid":"#"}
				document.getElementsByClassName('.inputfile').value = elem[0]
				var label	 = document.getElementById('but');
				label.querySelector( 'span' ).innerHTML = elem[1];
        document.getElementById("file-7").value = elem[1];
    }
}
function loadlib() {
  libarr = JSON.parse(sessionStorage.lib_array)
  const sel = document.getElementById("selectedlib");
  for (element of libarr) {
    var opt = document.createElement("option")
    opt.text = element
    sel.add(opt)
  }
}
function libtype_check() {
  libname = (document.getElementById("selectedlib")).value
  libarr = JSON.parse(sessionStorage.libs)
  if (libarr[libname][0]["istxt"] == 1) {
    document.getElementById("file-7").disabled = true;
    document.getElementById("but").style.cursor = "not-allowed";
    document.getElementById("decryptbutton").setAttribute("onclick", "decrypt_txt();");
  } else {
    //
  }
}
async function decrypt() {
  libname = (document.getElementById("selectedlib")).value
  path = (document.getElementById("file-7")).value;
  let decr = await eel.File_Decrypt(libname, path)()
  .then(decr => {
    x = decr
  })
  .catch(e => console.log(e));
  if (x==1) {
    //
  } else {
    eel.Mbox("Oopie!", "Somethings up and we just cant figure it out :(", 2)
  }
}
function decrypt_txt() {
  libname = (document.getElementById("selectedlib")).value;
  eel.Text_Decrypt(libname)();
}
