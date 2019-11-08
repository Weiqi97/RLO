$(function() {
    $("#get-comparison").click(function () {
        $.ajax({url: "/graph"})
            .done(function (result) {
                    $("#container").html(result)
                }
            )
    })
});
