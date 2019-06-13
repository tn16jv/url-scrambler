function copyField() {
  var copyText = document.getElementById("myInput");

  copyText.select();

  document.execCommand("copy");

  alert("Copied the text: " + copyText.value);
}

function postURL() {
    urlString = document.getElementById("longurl").value;
    $.ajax({
        data:'longuri=' + urlString,
        type: "POST",
        success:function(data){
            $("#ajaxArea").prepend(data);
        },
        error:function (){alert("failure");},
        async: true
    });
}