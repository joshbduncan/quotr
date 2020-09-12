// CLIPBOARD.JS COPY PERMALINK
var clipboard = new ClipboardJS('.btn');
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

// SHARE MODEL ON LIST VIEW
$('#shareModal').on('show.bs.modal', function (event) {
    var identifier = $(event.relatedTarget) // Button that triggered the modal
    var quote_link = identifier.data('identifier') // Extract info from data-* attributes

    var copy_permalink = document.getElementById("permalink")
    copy_permalink.setAttribute('value', quote_link)

    var email_permalink = document.getElementById("email-button")
    var email_link = "mailto:?subject=Check out this quote!&body=Hey, I found this quote and thought you might like it " + quote_link + "."
    email_permalink.setAttribute('href', email_link)
});


// UPDATE QUOTE LOVES
$(document).ready(function () {
    $('.quote-loves').on('click', function () {
        event.preventDefault();
        var quote_id = $(this).attr('quote_id');
        var love = $(this)[0]
        var love_button = love.getElementsByClassName('love_button')[0];
        var love_count = love.getElementsByClassName('love_count')[0];
        var love_action = love.getAttribute('love_action');

        req = $.ajax({
            url: '/quote/_loved',
            type: 'POST',
            data: { id: quote_id, action: love_action }
        });

        req.done(function (data) {
            if (love_action == "increase") {
                love_button.classList.remove("far");
                love_button.classList.add("fas");
                love.setAttribute('love_action', 'decrease');
                love_count.innerText = data.loves;
            } else {
                love_button.classList.remove("fas");
                love_button.classList.add("far");
                love.setAttribute('love_action', 'increase');
                love_count.innerText = data.loves;
            }
        });
    });
});