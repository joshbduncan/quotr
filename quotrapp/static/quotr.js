// CLIPBOARD.JS COPY PERMALINK
var clipboard = new ClipboardJS(".btn");
// var button = document.getElementById("copy-button");

clipboard.on('success', function (e) {
    // console.log(e)
    e.trigger.innerHTML = '<i class="fas fa-check"></i>';
    e.trigger.classList = 'btn btn-success';
    setTimeout(() => {
        e.trigger.innerHTML = '<i class="fas fa-copy"></i>';
        e.trigger.classList = 'btn btn-primary';
    }, 2000);
});

clipboard.on('error', function (e) {
    // console.log(e)
    e.trigger.innerHTML = '<i class="fas fa-times"></i>';
    e.trigger.classList = 'btn btn-danger';
    setTimeout(() => {
        e.trigger.innerHTML = '<i class="fas fa-copy"></i>';
        e.trigger.classList = 'btn btn-primary';
    }, 2000);
});

// SHARE MODEL
$("#shareModal").on("show.bs.modal", function (event) {
    var identifier = $(event.relatedTarget); // Button that triggered the modal
    var quote_link = identifier.data("identifier"); // Extract info from data-* attributes
    var quote_link_short = quote_link.replace(/^https?\:\/\//i, ""); // Remove http:// or https:// from URL
    var quote_text = identifier.data("content"); // Extract quote content from data-* attributes
    var quote_author = identifier.data("author"); // Extract quote author from data-* attributes

    var quote_length = quote_text.length;
    var author_length = quote_author.length;
    var link_length = quote_link_short.length;

    if (quote_length + author_length + link_length + 3 > 288) {
        var length = 288 - author_length - link_length - 10;
        var quote_text = quote_text.substring(0, length) + "...";
    }

    // Twitter Share Link details
    // https://tutorials.botsfloor.com/step-by-step-creating-share-to-twitter-links-66c255f4d5e7

    var twitter_content = encodeURIComponent(quote_text + " – " + quote_author + " ") + quote_link_short;
    var twitter_button = document.getElementById("twitter-button");
    var twitter_tweet = "https://twitter.com/intent/tweet?text=" + twitter_content.replace("title=", "");
    twitter_button.setAttribute("href", twitter_tweet);

    var facebook_button = document.getElementById("facebook-button");
    var facebook_link = "https://www.facebook.com/sharer/sharer.php?u=" + quote_link;
    facebook_button.setAttribute("href", facebook_link);

    var email_body = 'Hey, I found this quote and thought you might like it!\n\n' +
        '"' + quote_text + '"\n\n' +
        'View it online: ' + quote_link;

    var email_button = document.getElementById("email-button");
    var email_link = encodeURI("mailto:?subject=Check out this quote!&body=" + email_body);
    email_button.setAttribute("href", email_link);

    var copy_permalink = document.getElementById("permalink");
    copy_permalink.setAttribute("value", quote_link);

});


// UPDATE QUOTE LOVES
$(document).ready(function () {
    $(".quote-loves").on("click", function () {
        event.preventDefault();
        var quote_id = $(this).attr("quote_id");
        var love = $(this)[0];
        var love_button = love.getElementsByClassName("love_button")[0];
        var love_count = love.getElementsByClassName("love_count")[0];
        var love_action = love.getAttribute("love_action");

        req = $.ajax({
            url: "/quote/_loved",
            type: "POST",
            data: { id: quote_id, action: love_action }
        });

        req.done(function (data) {
            if (love_action == "increase") {
                love_button.classList.remove("far");
                love_button.classList.add("fas");
                love.setAttribute("love_action", "decrease");
                love_count.innerText = data.loves;
            } else {
                love_button.classList.remove("fas");
                love_button.classList.add("far");
                love.setAttribute("love_action", "increase");
                love_count.innerText = data.loves;
            }
        });
    });
});