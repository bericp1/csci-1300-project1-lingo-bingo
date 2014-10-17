(function ($) {
  'use strict';

  var $loading = $('.loading'),
    $table = $('table'),
    $body = $table.find('tbody');

  var $templates = {
    row: $body.find('tr').detach()
  };

  var generators = {
    row: function(game){
      var $row = $templates.row.clone();
      $row.data('game-id', game.id);
      $row.find('.game-started').html(new Date(game.started));
      $row.find('.game-finished').html(new Date(game.finished));
      $row.find('.game-score').html(game.score);
      $row.find('.game-rank').html(game.rank);
      $row.find('.game-player').html(game.player);
      return $row;
    }
  };

  $table.hide();

  $.get('/leaderboard', function(data){
    $.each(data.games, function(idx, game){
      $body.append(generators.row(game));
    });
    $loading.hide();
    $table.show();
  });

})(jQuery);