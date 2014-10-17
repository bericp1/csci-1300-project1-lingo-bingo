(function ($) {
  'use strict';

  var game = false,
    $jumbo = $('.jumbotron'),
    $loading = $('.loading'),
    $game = $('.game'),
    $qarea = $game.find('.q-area'),
    $info = $game.find('.info'),
    $name = $jumbo.find('input[type=text]').first();

  var $templates = {
    snippet: $game.find('.snippet-template').detach(),
    button: $game.find('.button-template').detach()
  };

  var generators = {
    snippet: function(id, snippet, poss){
      var $snippet = $templates.snippet.clone();
      $snippet.data('snippet-id', id);
      $snippet.find('textarea').val(snippet);
      var $buttons = $snippet.find('.btn-group');
      $.each(poss, function(idx, option){
        $buttons.append(generators.button(id, option));
      });
      return $snippet;
    },
    button: function(id, option){
      var $button = $templates.button.clone();
      $button.find('span').text(option);
      $button.find('input').attr('name', id).attr('value', option);
      return $button;
    }
  };

  var start_game = function(){
    var name = $name.val();
    $loading.find('span').text(name);
    $jumbo.hide();
    $loading.show();
    $.get('/start?player=' + encodeURIComponent(name), function(game) {
      if(game.status != 'ok'){
        var message = game.error || 'An unknown error occurred.';
        swal('There was an issue trying to start your game:\n\n' + message);
        $loading.hide();
        $jumbo.show();
      }else{
        $game.prepend($('<input type="hidden" name="game">').attr('value', game.id));
        $info.append('<strong>Game ID:</strong> <em>' + game.id + '</em><br>');
        $info.append('<strong>Player:</strong> <em>' + game.player + '</em><br>');
        $info.append('<strong>Created at:</strong> <em>' + new Date(game.created) + '</em><br>');
        $info.append('<strong>Populated with data at:</strong> <em>' + new Date(game.populated) + '</em><br>');
        $info.append('<strong>Started at:</strong> <em>' + new Date(game.started) + '</em><br>');
        $.each(game.turns, function(idx, turn){
          $qarea.append(generators.snippet(turn.id, turn.snippet, turn.possibilities))
        });
        $loading.hide();
        $game.show();
      }
    })
      .fail(function(){
        swal('Something bad happened when trying to start the game...');
        $loading.hide();
        $jumbo.show();
      });
  };

  $jumbo.on('click', 'button', function(ev){
    ev.preventDefault();
    start_game();
  });

  $game.on('submit', function(ev){
    ev.preventDefault();
    $.post($game.attr('action'), $game.serialize(), function(data){
      if(data.won){
        swal({
          title: 'You Won!',
          text:'Congrats ' + data.player + '!\n\nYour score was: ' + data.score + '\n(Lower scores are better)\n\nWhich ranks you at: ' + data.rank + '\n\nTaking you to the leaderboard...'
        }, function(){
          window.location.href = '/leaderboard.html';
        });
      }else{
        swal('Try Again!\n\nYou got ' + data.right + ' out of ' + data.total + ' correct.');
      }
    });
  });

  $loading.hide();
  $game.hide();

  //$('.btn').button()

})(jQuery);