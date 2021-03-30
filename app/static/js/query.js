function dataQueryAjax() {
    $.ajax (
        {
            url : "/",
            method : "post",
            cache : false,
            contentType : "application/json",
            data : JSON.stringify(
                {
                    "url" : $("#input").val(),
                    "created_at" : Date.now(),
                }
            ),
            complete : function(d) {
                data = JSON.parse(d.responseText)
                console.log(data)
                if (data["message"]) {
                    console.log(data)
                    $("#error_message").removeClass("invisible")
                    $("#error_message").text(data["message"])
                }
                else {
                    console.log("succuess")
                    $("#output").val(data["host"] + '/' + data["output"])
                }
            }
        }
    )
}
function alertReset() {
    $("#error_message").addClass("invisible")
}