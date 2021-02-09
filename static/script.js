$(".delete").click(function () {
    $("#content").empty();
    $("#bottombar").html("Right click on a mistake to show correction suggestions<div class=\"push\"></div>0 characters, 0 words  <i class=\"material-icons\">info</i>");
    $("#bottombar").css({
        "border-top": "1px solid #C0C0C0",
        "background": "white"
    });
});

$('#bottombar').on('mouseenter', 'i', function (e) {
    var top = e.pageY - 145;
    var left = e.pageX - 345;
    $("#tooltip").css({
        top: top + "px",
        left: left + "px",
        "visibility": "visible"
    });
}).on('mouseleave', 'i', function () {
    $("#tooltip").css({
        "visibility": "hidden"
    });
});

$(".grammar").click(grammarcheck);

function grammarcheck() {
    var content = $('#content').text();
    var language = $('#dropdown').val();
    var request = '/background_check';
    $("#app").addClass("loading");
    const data = {"content": content, "language": language}
    fetch(request, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify(data)
    }).then(function (response) {
        return response.json();
    }).then(function (json) {
        $('#content').html(json.content)
        $('#ngramcount').html(json.ngramcounts)
        var bottomdiv = json.errorcount + " Errors found" + "<div class='push'></div>" + json.tokencount + " characters, " + json.wordcount + " words  <i class=\"material-icons\">info</i>"
        $('#bottombar').html(bottomdiv)
        if (json.errorcount == "0") {
            $("#bottombar").css({
                "border-top-color": "rgba(0,255,0,.17)",
                background: "rgba(0,255,0,.05)"
            });
        } else {
            $("#bottombar").css({
                "border-top-color": "rgba(255,0,0,.15)",
                "background": "rgba(255,0,0,.05)"
            });
        }
        $("#app").removeClass("loading");
    });

};

$(document).ready(function () {

    // disable right click and show custom context menu
    $("#content").on('contextmenu', 'mark', function (e) {
        var id = this.id;
        $("#txt_id").val(id);

        var top = e.pageY + 5;
        var left = e.pageX;

        $("#context-ul").empty()
        var items = $("#" + id)[0].getAttribute('suggestions').split(" ");
        var scores = $("#" + id)[0].getAttribute('scores').split(" ");
        var ranks = $("#" + id)[0].getAttribute('ranks').split(" ");
        for (i = 0; i < items.length; i++) {
            if ($('#debug-check').prop('checked')) {
                $("#context-ul").append('<li>' + items[i] + ' : bert ' + scores[i] + ' : scores ' + ranks[i] + '</li>');
            } else {
                $("#context-ul").append('<li>' + items[i] + '</li>');
            }
        }
        // Show contextmenu
        $(".context-menu").toggle(100).css({
            top: top + "px",
            left: left + "px",
            display: "inline"
        });

        return false;
    });

// Hide context menu
    $(document).on('contextmenu click', function () {
        $(".context-menu").hide();
        $("#txt_id").val("");
    });

// disable context-menu from custom menu
    $('.context-menu').on('contextmenu', function () {
        return false;
    });

// Clicked context-menu item
    $('.context-menu').on('click', 'li', function () {
        var text = $(this).text();
        var id = $('#txt_id').val();
        $("#" + id).before(text);
        $("#" + id).remove();
        $(".context-menu").hide();
        grammarcheck();
    });

});

$('#debug-check').change(function () {
    if ($('#debug-check').prop('checked')) {
        var top = $("#grammarcontainer").position().top;
        var right = $("#grammarcontainer").position().top;
        $("#ngramcount").css({
            "visibility": "visible",
            "top": top,
        });
    } else {
        $("#ngramcount").css({
            "visibility": "hidden"
        });
    }
});
