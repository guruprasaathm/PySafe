function newaccount() {
	opwd = document.getElementById("pwdid").value
	cpwd = document.getElementById("cpwdid").value
	if (opwd == cpwd) {
		data = [document.getElementById('unameid').value, document.getElementById('pwdid').value, document.getElementById('mailid').value];
		eel.AddAccount(data)(function account_creation_status(stat) {
			if (stat==1) {
					eel.Mbox("Success!", "Your PySafe account has been \nsuccessfully created! Have at it champ!", 2)();
			} else if (stat==2) {
				eel.Mbox("Oopie!", "That account already exists! Please sign in instead!", 1)()
			} else {
				eel.Mbox("Oopie!", "Something's wrong, We couldn't \ncreate your account, Kindly try again.", 0)();
			}
		});
	} else {
		eel.Mbox("Oopie!", "The passwords must match!", 0)();
		document.getElementById('pwdid').value='';
		document.getElementById('cpwdid').value='';
	}
}
function clearfunc() {
	document.getElementById('unameid').value='';
	document.getElementById('pwdid').value='';
	document.getElementById('cpwdid').value='';
	document.getElementById('mailid').value='';
}
