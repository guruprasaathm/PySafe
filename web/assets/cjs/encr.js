function typeact() {
  var curtype = $('input[name="typesel"]:checked').val();
  if (curtype == "texttype") {
    $("#textcanvas").attr('placeholder', 'enter text to be encrypted')
    document.getElementById('setofsel') .style.visibility = "hidden"
    document.getElementById('setofsel') .style.display = "none"
    document.getElementById('textcanvas') .style.visibility = "hidden"
    document.getElementById('textcanvas') .style.display = "none"
    document.getElementById('textnput') .style.visibility = "visible"
    document.getElementById('textnput') .style.display = "flex"
  }
  else {
    document.getElementById('textnput') .style.visibility = "hidden"
    document.getElementById('textnput') .style.display = "none"
    document.getElementById('textcanvas') .style.visibility = "visible"
    document.getElementById('textcanvas') .style.display = "flex"
    document.getElementById('setofsel') .style.visibility = "visible"
    document.getElementById('setofsel') .style.display = "flex"
  }
}
async function fileselhandler(ele) {
    let a = await eel.fileinihandle(ele.id)()
    .then(a => {
        handledata(a);
    })
    .catch(e => console.log(e));
}
function handledata(data) {
    for (elem of data) {
        //var colormatch = {"foldid":"#000000", "docid":"#ffbb00", "imgid":"#052f9c", "vidid":"#a80032", "audid"::"#4300a8", "othid":"#"}
        labelx = "<div><label id='"+elem[0]+"lab' onclick='removefile(this);'><span style='cursor: grab'><h5 style='font-family: 'secular one'>"+elem[0]+"</h5></span></label><br></div>"
        $("#textcanvas").append(labelx);
        patharr.root.push(elem[1]);
    }
}
function removefile(id) {
    (id.parentNode).style.display = "none";
    (id.parentNode).remove();
}
async function encryptroot() {
  document.getElementById("encrybut").disabled = true;
  if ((document.getElementById("libnameinput").value).length > 0) {
    lib_name = document.getElementById("libnameinput").value
    const to_mongo = (document.getElementById("mongoToggle")?.checked === true);
    if (document.getElementById("filerad").checked) {
      if (patharr.root.length > 0) {
        document.getElementById("textcanvas").innerHTML=''
        RootFrame = document.getElementById("encrframeroot");
        RootFrame.setAttribute("style", "cursor: wait;")
        let encr = await eel.File_Encrypt(lib_name, patharr.root, to_mongo)()
        .then(encr => {
          x = encr
        })
        .catch(e => console.log(e));
        if (x==1) {
          eel.Mbox("Done!", "Your stuff has been encrypted Successfully :)", 2)
        } else {
          eel.Mbox("Oopie!", "Somethings up and we just cant figure it out :(", 2)
        }
        RootFrame.setAttribute("style", "cursor: default;")
      } else if (patharr.root.length == 0) {
        eel.Mbox("Oopie!", "You need to select a file a first!", 1)
      } else {
        eel.Mbox("Oopie!", "Somethings up and we just cant figure it out :(", 2)
      }
    } else {
      if ((document.getElementById("textnput").value).length > 0) {
        enctext = ''
        enctext = enctext + document.getElementById("textnput").value
        libname = document.getElementById("libnameinput").value
        document.getElementById("libnameinput").value=''
        document.getElementById("textnput").value=''
        let encr = await eel.Text_Encrpyt(libname, enctext, to_mongo)()
        .then(encr => {
            x = encr
        })
        .catch(e => console.log(e));
        if (x==1) {
          eel.Mbox("Done!", "Encrytped Successfully!", 2)
        } else {
          eel.Mbox("Oopie!", "Somethingsree up and we just cant figure it out :(", 2)
        }
      } else if (patharr.root.length == 0) {
        eel.Mbox("Oopie!", "You need to enter something in there!", 1)
      } else {
        eel.Mbox("Oopie!", "Somethings up and we just cant figure it out :(", 2)
      }
    }
  }
  document.getElementById("encrybut").disabled = false;
}
function clearfunc() {
    document.getElementById("libnameinput").value='';
    if (document.getElementById("filerad").checked) {
        document.getElementById("textcanvas").innerHTML=''
        patharr  = {"root":[]};
    } else {
        document.getElementById("textnput").value=''
    }
}
window.patharr  = {"root":[]};
window.enctext = "";
