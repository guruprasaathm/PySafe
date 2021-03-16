function filter(ujson) {
	unfiltered_raw_json = ujson
	double_quoted_json = unfiltered_raw_json.replace(/'/g, '"');
	realjson = JSON.parse(double_quoted_json)
	return realjson
	//realjson = JSON.parse((sessionStorage.udata.replace(/'/g, '"')).substr(1, (sessionStorage.udata.replace(/'/g, '"').length - 2)));
}
function fetchindex() {
	eel.GetUserIndex(sessionStorage.guname,sessionStorage.gpwd)()
	.then(a => {
		SJSON = JSON.stringify(filter(a))
		FJSON = (JSON.parse(SJSON))
		sessionStorage.ac_create_time = FJSON.ac_create_time
		sessionStorage.mail = FJSON.mail
		sessionStorage.lib_array = JSON.stringify(filter(JSON.stringify(FJSON.library_index.lib_array)))
		sessionStorage.lib_count = FJSON.library_index.lib_count
		libs = filter(JSON.stringify(FJSON.library_index.edges))
		sessionStorage.libs = JSON.stringify(libs)
	})
	.catch(thiserror => console.log(thiserror));
}
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
function logout() {
	sessionStorage.clear();
	eel.logout_clear()();
	window.location.href='index.html'
}
