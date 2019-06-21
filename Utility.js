function copyField(elementId) {
  var copyText = document.getElementById(elementId);

  copyText.select();

  document.execCommand('copy');

  alert('Copied: ' + copyText.value);
}

function postURL() {
    urlString = document.getElementById('longurl').value;
    var loader = $('<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>');
    $('#submitButton').text('');
    $('#submitButton').append(loader);
    $('#submitButton').prop('disabled', true);
    $.ajax({
        data:'longuri=' + urlString,
        type: 'POST',
        timeout: 5000,
        success:function(data){
            try {
                var jsonData = JSON.parse(data)
                $('#ajaxArea').prepend(createLinkDiv(jsonData.longurl, jsonData.shorturl));
            } catch (e) {
                var errorDiv = $('<div class="d-flex justify-content-center mb-3 mt-3"></div>').text(data);
                $('#ajaxArea').prepend(errorDiv);
            }
            },
        error:function (xhr, status){
            alert('Server Issue: ' + status);
            },
        async: true
    }).always(function() {    // Want to re-enable the button regardless of success or failure.
        $('#submitButton').empty();
        $('#submitButton').text('Submit');
        $('#submitButton').removeAttr('disabled');
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
    var label = $('<label></label>').text('Scrambled URL for: ');
    var link = $(`<a target="_blank" href=${shorturl}></a>`).text(`${longurl}`);
    label.append(link)
    var input = $(`<input type='url' class='form-control' size="80" readonly value=${shorturl} id=${shorturl}>`);
    var button = $(`<button onclick='copyField("${shorturl}")' class='btn btn-info'></button>`).text('Copy URL');
    var linkDiv = $('<div class="form-group mb-3 mt-3"></div>').append(label).append(input).append(button);
    linkDiv = $('<div class="d-flex justify-content-center"></div>').append(linkDiv);
    return linkDiv;
}