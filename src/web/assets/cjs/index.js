async function signinvalidate() {
	uname = document.getElementById("UserNameId").value;
	pwd = document.getElementById("PasswordID").value;
	sessionStorage.guname = uname
	sessionStorage.gpwd = pwd
	eel.LoginValidation(uname, pwd)(function(stat) {
		if (stat==1) {
			window.location.href='./sign_in_wait.html';
		} else if (stat==0) {
			eel.Mbox("Oopie!", "Your password is incorrect!", 0)();
		} else if (stat==-1) {
			eel.Mbox("Oopie!", "Unhandled exception, Sorrie!", 0)();
		} else if (stat==-2) {
			eel.Mbox("Oopie!", "That account does not exist!", 1)();
		} else {
			eel.Mbox("Oopie!", "Unhandle exception, Sorrie!", 0)();
		}
	});
}
function index_ini() {
	eel.mkindex()
}
