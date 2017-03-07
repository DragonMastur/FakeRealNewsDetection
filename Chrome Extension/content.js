chrome.runtime.sendMessage({"name": "content.js", "command": "send-url"}, function(response) {
    var news_type = JSON.parse(response.result).news_type;
    if (news_type == "Real") {
        alert("FAKE-REAL NEWS DETECTOR USING ML: This page should contain reliable information.");
    } else if (news_type == "Fake") {
        alert("FAKE-REAL NEWS DETECTOR USING ML: This page doesn't contain reliable information. This article may include propoganda and fake news.");
    } else if (news_type == "Caution") {
        alert("FAKE-REAL NEWS DETECTOR USING ML: This articles contents could not be determined. Use caution while reading.");
    } else {
        alert("FAKE-REAL NEWS DETECTOR USING ML: There was an error. Check your internet connection and try again. To disable this extension go to 'chrome://extensions' and uncheck the 'Enabled' box.");
    }
});

chrome.runtime.sendMessage({"name": "content.js", "command": "get-storage", "key": "seml_sites"}, function(response) {
    console.log(response);
});

chrome.runtime.sendMessage({"name": "content.js", "command": "get-storage", "key": "seml_options"}, function(response) {
    console.log(response);
});
