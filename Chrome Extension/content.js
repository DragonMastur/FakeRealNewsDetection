//var firstHref = $("a[href^='http']").eq(0).attr("href");
chrome.tabs.query({'active': true}, function(tabs) {
    var firstHref = tabs[0].url;
});

console.log(firstHref);
