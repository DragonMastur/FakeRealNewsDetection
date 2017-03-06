chrome.runtime.sendMessage({"name": "content.js", "command": "send-url"}, function(response) {
    console.log("This page contains " + response.result);
});

chrome.runtime.sendMessage({"name": "content.js", "command": "get-storage", "key": "seml_sites"}, function(response) {
    console.log(response);
});

chrome.runtime.sendMessage({"name": "content.js", "command": "get-storage", "key": "seml_options"}, function(response) {
    console.log(response);
});
