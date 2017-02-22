console.log("Started 'Fake News Detector'");

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        console.log("Got request from content script: " + sender.tab.url);
        console.log("Request was: " + JSON.stringify(request));
        if (request.command == "get-url-current") {
            sendResponse({"result": sender.tab.url});
        }
        if (request.command == "send-url") {
            $.post("http://piist300.pythonanywhere.com/seml/get", {"url": sender.tab.url}).done(function(data) {
                console.log("Got data from server! Data: " + JSON.stringify(data));
                sendResponse({"result": data});
            });
        }
});
