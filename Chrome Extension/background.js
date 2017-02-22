console.log("Started 'Fake News Detector'");

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        console.log("Got request from content script: " + sender.tab.url);
        console.log("Request was: " + JSON.stringify(request));
        if (request.command == "get-url-current")
            sendResponse({"result": sender.tab.url});
});
