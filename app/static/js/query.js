function getShortenAjax() {
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
                if (data["message"]) {
                    $("#error_message").removeClass("invisible")
                    $("#error_message").text(data["message"])
                }
                else {
                    $("#error_message").addClass("invisible")
                    $("#output").val(data["host"] + "/" + data["output"])
                    getStatsAjax(0);
                }
            }
        }
    )
}
function alertReset() {
    $("#error_message").addClass("invisible")
}
function getStatsAjax(p) {
    $.ajax (
        {
            url : "/stats",
            method : "get",
            cache : true,
            data : {
                    "page" : p,
                    "limit" : 5
            },
            complete : function(d) {
                $("#stat_section").empty()
                data = JSON.parse(d.responseText)["output"]
                for (i = 0; i < data.length; i ++) {
                    d = data[i]
                    StatFactory(
                        d["key"], 
                        d["url"],
                        new Date(parseInt(d["created_at"])).formatted(),
                        d["last_viewed"] ? new Date(parseInt(d["last_viewed"]+"000")).formatted() : "-",
                        d["pageview"] ? d["pageview"] : 0
                    )
                }
            }
        }
    )
}

function StatFactory(s, f, c, l, ct) {
    $("#stat_section").append(
        $("<div>", {"class" : "card"}).append(
            $("<div>", {"class" : "row card-body"}).append(
                $("<div>", {"class" : "col-md-10"}).append(
                    $("<h3>", {"class" : "card-title"}).text(s)
                ).append(
                    $("<p>", {"class" : "card-text text-truncate"}).text(f)
                ).append(
                    $("<div>", {"class" : "d-flex justify-content-between"}).append(
                        $("<span>", {"class" : "sub-note"}).text("created at : " + c)
                    ).append(
                        $("<span>", {"class" : "sub-note"}).text("last visited : " + l)
                    )
                )
            ).append(
                $("<div>", {"class" : "col-md-2 "}).append(
                    $("<button>", {"class" : "btn btn-light ml-auto"}).attr("disabled", true).append(
                        $("<i>", {"class" : "fa fa-eye"})
                    ).append(
                        $("<div>", {"class" : "ml-1"}).append(
                            $("<span>").text(ct)
                        )
                    )
                )
            )
            
        )
    )
}
function kFormatter(num) {
    return Math.abs(num) > 999 ? Math.sign(num)*((Math.abs(num)/1000).toFixed(1)) + 'k' : Math.sign(num)*Math.abs(num)
}
Date.prototype.formatted = function() {
    var mm = this.getMonth() + 1; // getMonth() is zero-based
    var dd = this.getDate();
    var hh = this.getHours();
    var min = this.getMinutes();
    var ss = this.getSeconds();
  
    return [this.getFullYear(),
            (mm>9 ? "" : "0") + mm,
            (dd>9 ? "" : "0") + dd
           ].join("-") + " " + [
               (hh>9 ? "" : "0") + hh,
               (min>9 ? "" : "0") + min, 
               (ss>9 ? "" : "0") + ss
           ].join(":")
};

function updateStats(interval) {
    if (parseInt($("#stat_section").attr("page")) == 0) {
        console.log("check")
        getStatsAjax(0);
    }
}

getStatsAjax(0);
setInterval(function(){updateStats(10)}, 600*1000);