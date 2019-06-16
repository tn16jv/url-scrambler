function copyField(elementId) {
  var copyText = document.getElementById(elementId);

  copyText.select();

  document.execCommand('copy');

  alert('Copied: ' + copyText.value);
}

function postURL() {
    urlString = document.getElementById('longurl').value;
    $.ajax({
        data:'longuri=' + urlString,
        type: 'POST',
        success:function(data){
            try {
                var jsonData = JSON.parse(data)
                $('#ajaxArea').prepend(createLinkDiv(jsonData.longurl, jsonData.shorturl));
            } catch (e) {
                var errorDiv = $('<div class="mb-4"></div>').text(data);
                $('#ajaxArea').append(errorDiv);
            }
        },
        error:function (){alert('Could not create URL');},
        async: true
    });
}

$(document).ready(function() {
    $.ajax({
        url:'/PastUrls',
        type: 'GET',
        success:function(data){
            var jsonData = JSON.parse(data)
            var longurl, shorturl
            for (var key in jsonData) {
                longurl = key
                shorturl = jsonData[key]
                $('#pastUrlsArea').append(createLinkDiv(longurl, shorturl));
            }
        },
        error:function (){alert('failure');},
        async: true
    });
});

function createLinkDiv(longurl, shorturl) {
    var label = $('<label></label>').text(`Scrambled URL for: ${longurl}`);
    var input = $(`<input type='url' class='form-control' value=${shorturl} id=${shorturl}>`);
    var button = $(`<button onclick='copyField("${shorturl}")' class='btn btn-info'></button>`).text('Copy URL');
    var linkDiv = $('<div class="mb-4"></div>').append(label).append(input).append(button);
    return linkDiv;
}