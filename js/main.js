var last_card_played = false;
var chair_id = -1;

var short_name_team1 = 'T1';
var short_name_team2 = 'T2';
var name_team1 = 'Team 1';
var name_team2 = 'Team 2';

function display(cards, div, cb = null) {
    document.getElementById(div).innerHTML = '';
    for(var i = 0; i < cards.length; i++) {
        var card = document.createElement("div");
        var value = document.createElement("div");
        var suit = document.createElement("div");
        card.className = "card";
        value.className = "value";
        if (cards[i] != null) {
            suit.className = "suit " + cards[i]['suit'];

            card.setAttribute('suit', cards[i]['suit'])
            card.setAttribute('value', cards[i]['value'])

            value.innerHTML = cards[i]['value'];
            card.appendChild(value);
            card.appendChild(suit);

            if (cb != null) {
                card.addEventListener('click', cb);
            }
        } else {
            card.className += ' null'
            suit.className = "suit null";
            value.innerHTML = '&nbsp';
            card.appendChild(value);
            card.appendChild(suit);
        }
        document.getElementById(div).appendChild(card);
    }
}
function display_cards(cards) {
    display(cards, 'hand', function() {
        let s = this.getAttribute('suit');
        let v = this.getAttribute('value');
        send_msg('play', { 'value': v, 'suit': s, 'chair': chair_id });
        if (!last_card_played) {
            last_card_played = true;
            this.remove();
        }
    })
}

function display_table(cards) {
    display(cards, 'table');

    if (cards.length == 4) {
        $('#team1').removeClass('disable');
        $('#team2').removeClass('disable');
    }
}

function display_last_hand(cards) {
    display(cards, 'last_hand');
}

function display_results(cards1, cards2) {
    document.getElementById('hand').innerHTML = '';
    document.getElementById('table').innerHTML = '';
    document.getElementById('last_hand').innerHTML = '';
    display(cards1, 'res1');
    display(cards2, 'res2');
    $('#res1').prepend(`<h3>${name_team1}</h3><br>`);
    $('#res2').prepend(`<h3>${name_team2}</h3><br>`);
}

var seated = 0;
function reset() {
    console.log('reset')
    document.getElementById('hand').innerHTML = '';
    document.getElementById('table').innerHTML = '';
    document.getElementById('last_hand').innerHTML = '';
    document.getElementById('res1').innerHTML = '';
    document.getElementById('res2').innerHTML = '';
    $('#team1').addClass('disable');
    $('#team2').addClass('disable');
    $('#res1').addClass('disable');
    $('#res2').addClass('disable');

    ['#chair1', '#chair3', '#chair2', '#chair4'].forEach(function (elem) {
        $(elem).removeClass('yours');
        $(elem).removeClass('taken');
        $(elem).addClass('free');
    });
    $('#order').html(`<div class="valign">XX</div>`);
    $('#order').html(`<div class="valign">XX</div>`);
    last_card_played = false;
    seated = 0;

    display_table([null,null,null,null]);
    display_last_hand([null,null,null,null]);
}


function load() {
    send_msg('user', {});

    document.getElementById("team1").addEventListener('click', function() {
        send_msg('pickup', 1);
    })
    document.getElementById("team2").addEventListener('click', function() {
        send_msg('pickup', 2);
    })
    document.getElementById("ok").addEventListener('click', function() {
        send_msg('newgame', {});
    })
    document.getElementById("chair1").addEventListener('click', function() {
        if (seated == 0) {
            seated = 1
            send_msg('chair', 0);
        }
    })
    document.getElementById("chair2").addEventListener('click', function() {
        if (seated == 0) {
            seated = 1
            send_msg('chair', 1);
        }
    })
    document.getElementById("chair3").addEventListener('click', function() {
        if (seated == 0) {
            seated = 1
            send_msg('chair', 2);
        }
    })
    document.getElementById("chair4").addEventListener('click', function() {
        if (seated == 0) {
            seated = 1
            send_msg('chair', 3);
        }
    })
    
    $("#team1").html(`<div class="valign">${name_team1}</div>`);
    $("#team2").html(`<div class="valign">${name_team2}</div>`);
}

window.onload = load;