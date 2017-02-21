var toggle_type;

function get_toggle_type() {
    toggle_type = localStorage["seml_toggle_type"];
    if (toggle_type == undefined) {
        toggle_type = "off";
        save_toggle_type();
    }
}

function save_toggle_type() {
    localStorage["seml_toggle_type"] = toggle_type;
}

function update_toggle() {
    get_toggle_type();
    $("#toggle-detection").val("Turn " + toggle_type + " detection for all sites.");
}

$("#toggle-detection").click(function() {
    if (toggle_type == "off") {
        toggle_type = "on";
    } else {
        toggle_type = "off";
    }
    save_toggle_type();
    update_toggle();
});

update_toggle();
