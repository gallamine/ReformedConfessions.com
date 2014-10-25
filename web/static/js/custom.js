function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


d3.json("data/wcf.json", function(wcf) {
    var lhs = d3.select("#lhs");
    lhs.append("ol")
        .selectAll("li")
        .data(d3.values(wcf))
        .enter()
        .append("li")
        .text(function(s, i) {
            return s["title"];
        })
        .on("click", function(s, i) {
            var params = {
                doc: 'wcf',
                chapter: i
            };
            query = $.param(params);
            document.write(query);

            // window.location.href = newUrl;
        });

    var document = getParameterByName("doc");
    var chapter = getParameterByName("chapter");
    var body = d3.select("#body");
    body.append("h3").text("Chapter " + chapter);

    body.selectAll("p")
        .data(wcf[chapter].body)
        .enter()
        .append("p")
        .text(function(s, i) {
            return [i + 1, s].join(". ");
        });

});