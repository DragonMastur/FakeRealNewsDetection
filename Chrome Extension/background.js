console.log("Started 'Fake News Detector'");

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        console.log("Got request from script: " + request.name);
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
        if (request.command == "get-storage") {
            console.log("Trying to get data with key '" + request.key + "'");
            try {
                sendResponse({"result": chrome.storage.sync.get(request.key)});
            } catch (err) {
                console.log("Failed to get data. "+err);
                sendResponse({"result": undefined, "error": err});
            }
        }
        if (request.command == "set-storage") {
            chrome.storage.sync.set(request.data, function() {
                console.log("Saved data: " + request.data);
                sendResponse("Saved!");
            })
        }
});
