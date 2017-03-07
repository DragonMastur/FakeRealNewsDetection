var storage_get;

console.log("Started 'Fake News Detector'");

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        console.log("Got request from script: " + request.name);
        console.log("Request was: " + JSON.stringify(request));
        if (request.command == "get-url-current") {
            sendResponse({"result": sender.tab.url});
        }
        if (request.command == "send-url") {
            $.get("https://ratb6it5gj.execute-api.us-west-2.amazonaws.com/dev/fakenews/analyze", {"url": sender.tab.url}).done(function(data) {
                console.log("Got data from server! Data: " + JSON.stringify(data));
                sendResponse({"result": JSON.stringify(data)});
            });
        }
        if (request.command == "get-storage") {
            console.log("Trying to get data with key '" + request.key + "'");
            try {
                chrome.storage.sync.get(request.key, function(data) {
                    console.log("Data collected successfully.");
                    storage_get = data;
                    sendResponse({"result": storage_get});
                });
            } catch (err) {
                console.log("Failed to get data. "+err);
                sendResponse({"result": undefined, "error": err});
            }
        }
        if (request.command == "set-storage") {
            chrome.storage.sync.set(JSON.parse(request.data), function() {
                console.log("Saved data: " + request.data);
                sendResponse("Saved!");
            })
        }
        if (request.command == "log") {
            console.log(request.log);
            sendResponse("Logged.");
        }
        return true;
});
