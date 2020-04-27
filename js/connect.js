var playing = true
function send_msg(event, val) {
   console.log(`Send event ${event} to server`);
   if (playing) {
      wssend(`${event}?${JSON.stringify(val)}`);
   }
}

var ws = null;
function wssend(msg) {
   if ("WebSocket" in window) {
      if (ws == null) {
         ws = new WebSocket("ws://2.7.115.129:8765");


         ws.onopen = function() { console.log('WebSocket openned.'); ws.send(msg) };

         ws.onmessage = function (evt) {
            var msg = JSON.parse(evt.data);

            console.log(`Message (type: ${msg['type']}) received.`);
            switch (msg['type']) {
               case 'ack':
                  console.log('Ack received', msg['type'], msg);
                  playing = msg['playing']
                  if (!msg['playing']) {
                     $('#spectator').show();
                  } else {
                     $('#pname').show()
                  }
                  display_table(msg['cards']);
                  display_last_hand(msg['last']);
                  break;
               case 'player':
                  if (msg['lplayers'] != 0) {
                     $('#room').html(`<div class="valign">Waiting for ${msg['lplayers']} players...</div>`);
                  } else if (msg['lchairs'] != 0) {
                     $('#room').html(`<div class="valign">Waiting for ${msg['lchairs']} seats...</div>`);
                  } else {
                     $('#room').hide();
                  }
                  update_players(msg['players'])
                  display_table(msg['cards']);
                  display_last_hand(msg['last']);
                  break;
               case 'yours':
                  chair_id = msg['chair'];
                  $('#chair'+msg['chair']).removeClass('free');
                  $('#chair'+msg['chair']).addClass('yours');
                  if ([1,3].indexOf(msg['chair']) != -1) {
                     $('#order').html(`<div class="valign">${short_name_team1}</div>`);
                  } else {
                     $('#order').html(`<div class="valign">${short_name_team2}</div>`);
                  }
                  seated = 2
                  break;
               case 'nope':
                  seated = 0
                  break;
               case 'cards':
                  $('#room').addClass('disable');
                  $('#team1').addClass('disable');
                  $('#team2').addClass('disable');
                  $('#res1').addClass('disable');
                  $('#res2').addClass('disable');
                  $('#ok').addClass('disable');
                  $('#ok').removeClass('clicked');
                  ['#chair1', '#chair3', '#chair2', '#chair4'].forEach(function (elem) {
                     $(elem).removeClass('played');
                  });
                  display_cards(msg['cards']);
                  display_table([null,null,null,null]);
                  display_last_hand([null,null,null,null]);
                  break;
               case 'newtable':
                  $('#team1').addClass('disable');
                  $('#team2').addClass('disable');
                  last_card_played = false;
                  ['#chair1', '#chair3', '#chair2', '#chair4'].forEach(function (elem) {
                     $(elem).removeClass('played');
                  });
               case 'table':
                  display_table(msg['cards']);
                  display_last_hand(msg['last']);
                  $('#chair'+msg['chair']).addClass('played');
                  break;
               case 'final':
                  $('#res1').removeClass('disable');
                  $('#res2').removeClass('disable');
                  $('#ok').removeClass('disable');
                  display_results(msg['team1'], msg['team2'], msg['der']);
                  ['#chair1', '#chair3', '#chair2', '#chair4'].forEach(function (elem) {
                     $(elem).removeClass('played');
                  });
                  break;
               case 'reset':
                  reset();
                  break;
               default:
                  console.log('UnManaged Received msg', msg['type']);
            }
         };

         ws.onclose = function() { console.log('WebSocket closed.'); ws = null; };
      } else {
         ws.send(msg)
      }

   } else {
      console.log("WebSocket NOT supported by your Browser!");
   }
}
