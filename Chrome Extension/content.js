chrome.runtime.sendMessage({"command": "get-url-current"}, function(response) {
    console.log("This page's URL is: " + response.result);
});
