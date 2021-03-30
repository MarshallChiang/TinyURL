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

function StatFactory(s, f, c, l, ct) {

    return $("<div>", {"class" : "card"}).append(
        $("<div>", {"class" : "card-body"}).append(
            $("<h5>", {"class" : "card-title"}).text(s)
        ).append(
            $("<p>", {"class" : "card-text"}).text(f)
        ).append(
            $("<div>", {"class" : "d-flex justify-content-between"}).append(
                $("<span>").text(c)
            ).append(
                $("<span>").text(l)
            ).append(
                $("<span>").text(ct)
            ) 
        )
    )
}
