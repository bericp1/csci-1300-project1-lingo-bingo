'''
Brandon Eric Phillips
06 October 2014
Madhu
Project 1
Lingo Bingo
'''

import os, random, string
from flask import Flask, Response, request, jsonify
import bson

from models import *

app = Flask(__name__, static_url_path='')

mongodb_url = os.environ.get('MONGOLAB_URI', False)
if mongodb_url: connect('lingobingo', host=mongodb_url)
else: connect('lingobingo')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', False)
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = ''.join(random.choice(string.ascii_letters + string.digits + '!_-$#@') for _ in range(8))
    print('\nPassword for admin interface (auto-generated):\t' + ADMIN_PASSWORD)
    print('To set a password explicitly, start the server with an ADMIN_PASSWORD environment variable.\n')

@app.route('/')
def home_serve():
    return app.send_static_file('index.html')

def shuffled(l):
    """Returns a copy of an array randomly shuffled"""
    return sorted(l, key=lambda k: random.random())

@app.route('/start')
def start():
    try:
        game = Game()
        game.player = request.args.get('player').strip()
        game.validate()
        game.populate(2)
        game.validate()

        turns = []
        random.shuffle(game.snippets)
        for snippet in game.snippets:
            poss = [snippet.language]
            poss += shuffled([lang for lang in game.languages if lang != snippet.language])[:3]
            turns.append({
                'id': str(snippet.id),
                'snippet': snippet.text,
                'possibilities': shuffled(poss)
            })
        game.start()
        game.save()

        return jsonify(
            status='ok',
            id=str(game.id),
            created=game.created,
            populated=game.populated,
            started=game.started,
            turns=turns,
            player=game.player
        )
    except (ValidationError, AttributeError) as e:
        return jsonify(
            status='bad',
            error='A player name must be provided that consists of at least three alphanumeric characters and spaces: ' + str(e.message)
        )

@app.route('/submit', methods = ['POST'])
def submit():
    data = dict(request.form.items())
    game = Game.objects(id=data.get('game'))[0]
    data.pop('game', None)

    total = len(data)
    right = 0
    for snippet in game.snippets:
        if snippet.id in data and data.get(snippet.id) == snippet.language:
            right += 1
    won = (right == total)

    if won:
        game.finish()
        game.save()
        return jsonify(won=True, score=game.score, player=game.player, rank=game.get_rank())
    else:
        return jsonify(won=False, total=total, right=right)

@app.route('/leaderboard')
def board():
    query = Game.rank_query()
    ranked_games = []
    rank = 1
    for game in query:
        game.rank = rank
        ranked_games.append(game)
        rank += 1
    return jsonify(games=[{'id':str(game.id),'started':game.started,'finished':game.finished,'score':game.score,'player':game.player,'rank':game.rank} for game in ranked_games])

@app.route('/admin')
def admin():
    """The admin API endpoint"""
    return Response(status=204)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('APP_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)