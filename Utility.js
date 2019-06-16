function copyField(elementId) {
  var copyText = document.getElementById(elementId);

  copyText.select();

  document.execCommand("copy");

  alert("Copied: " + copyText.value);
}

function postURL() {
    urlString = document.getElementById("longurl").value;
    $.ajax({
        data:'longuri=' + urlString,
        type: "POST",
        success:function(data){
            $("#ajaxArea").prepend(createLinkDiv(data));
        },
        error:function (){alert("failure");},
        async: true
    });
}

function createLinkDiv(urlData) {
    try {
        var json = JSON.parse(urlData)
        var label = $("<label></label>").text("Scrambled URL for " + json.longurl);
        var input = $("<input type='url' class='form-control' value=' " + json.shorturl + " ' + id ='" + json.shorturl + "'>");
        var button = $("<button onclick='copyField(\"" + json.shorturl +"\")' class='btn btn-info'></button>").text("Copy URL");
        var linkDiv = $("<div></div>").append(label).append(input).append(button);
        return linkDiv;
    } catch (e) {
        return $("<div></div>").text(urlData);
    }
}