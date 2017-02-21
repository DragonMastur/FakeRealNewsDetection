var toggle_type = "off";

function get_toggle_type() {
    try {
        chrome.storage.sync.get("seml_toggle_type", function(o) {
            toggle_type = o."seml_toggle_type"
        });
    } catch(err) {
        toggle_type = "off";
        save_toggle_type();
    }
}

function save_toggle_type() {
    chrome.storage.sync.set({"seml_toggle_type": toggle_type}, function() {
        console.log("Saved toggle type.");
    });
}

function update_toggle() {
    $("#toggle-detection").val("Turn " + toggle_type + " detection for all sites.");
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
