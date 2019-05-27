function clickTopBar(currentID) {

    $("#fade").fadeIn(5);
    storyflag = currentID == "#story"

    $(".box:not(" + currentID + "box):not(#storybox)").hide(5, "linear");
    if (!storyflag)
        $("#storywrapper").hide(5, "linear");

    var IDS = ["#dict", "#story", "#details"]
    IDS = IDS.splice(IDS.indexOf(currentID), 1)

    $(".toggled:not(" + currentID + ")").removeClass("toggled");
    $(currentID).toggleClass("toggled")
    if (!storyflag)
        $(currentID + "box").fadeToggle(5, "linear");
    else
        $(currentID + "wrapper").fadeToggle(5, "linear");

    var toggle = $(IDS[0]).hasClass("toggled") || $(IDS[1]).hasClass("toggled") || $(IDS[2]).hasClass("toggled");
    if (!toggle) {
        $("#fade").fadeOut(5);
    }
}

function switcher() {
    console.log("this")
    // $("#kanji").hide();
    // $("#strokes").show();
}

$(document).ready(function () {

    $("#dict").on("click", function () { clickTopBar("#dict") });
    $("#story").on("click", function () { clickTopBar("#story") });
    $("#details").on("click", function () { clickTopBar("#details") });
    $("#kanji").on("click", function () { switcher() });
    $("#strokes").on("click", function () { switcher() });
});