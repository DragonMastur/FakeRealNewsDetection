var sites;
var sites_list = $("#sites-list-ul");
var sites_inputs;

function get_sites() {
    chrome.runtime.sendMessage({"command": "get-storage", "key": "seml_sites"}, function(response) {
        console.log(response);
        sites = JSON.parse(response.result);
    });
    if (sites == undefined) {
        sites = {"0":{"url": "http:/null.com/none", "checked": true, "type": "Fake"}};
        save_sites();
    }
}
function save_sites() {
    chrome.runtime.sendMessage({"command": "set-storage", "data": JSON.stringify(sites)});
}

function load_options(ct) {
    get_sites();
    sites_list.empty();
    for (var s in sites) {
        var new_elm = document.createElement("input");
        new_elm.type = "checkbox";
        new_elm.value = sites[s].url;
        new_elm.id = "site-"+s;
        if (ct != undefined) {
            sites[s].checked = ct
            new_elm.checked = ct;
        } else {
            new_elm.checked = sites[s].checked
        }
        var new_elm_text = document.createElement("label");
        new_elm_text.htmlFor = "site-"+s;
        new_elm_text.append(document.createTextNode(sites[s].url));
        sites_list.append(new_elm);
        sites_list.append(new_elm_text);
        sites_list.append(document.createElement("br"));
        $("#site-"+s).change(function() {
            sites[this.id.split('-')[1]].checked = this.checked;
        });
    }
}

$("#save-options").click(function() {
    save_sites()
});

$("#sites-select-all").click(function() {
    load_options(true);
});

$("#sites-select-none").click(function() {
    load_options(false);
});
