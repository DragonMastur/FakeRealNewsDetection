chrome.runtime.sendMessage({"command": "send-url"}, function(response) {
    console.log("This page contains " + response.result);
});
