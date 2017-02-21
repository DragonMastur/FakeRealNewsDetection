var toggle_type = "off";

function update_toggle() {
    $("#toggle-detection").val("Turn " + toggle_type + " detection for this site.");
}

$("#toggle-detection").click(function() {
    if (toggle_type == "off") {
        toggle_type = "on";
    } else {
        toggle_type = "off";
    }
    update_toggle();
});

update_toggle();
