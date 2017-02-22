var sites;
var sites_list = $(".sites-list");

function get_sites() {
    try {
        sites = JSON.parse(localStorage["seml_sites"]);
    } catch(err) {
        sites = {0: {"url": "http://google.com/", "type": "Real"}};
        save_sites();
    }
}
function save_sites() {
    localStorage["seml_sites"] = JSON.stringify(sites);
}

function load_options() {
    get_sites();
    sites_list.empty();
    for (var s in sites) {
        var new_elm = document.createElement("input:checkbox");
        new_elm.textContent = sites[s]["url"];
        new_elm.checked = true;
        sites_list.append(new_elm);
        console.log(new_elm);
    }
}
