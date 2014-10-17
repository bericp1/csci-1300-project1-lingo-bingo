'''
Brandon Eric Phillips
06 October 2014
Madhu
Project 1
Lingo Bingo
'''

# Import some needed libraries
import os, random
from flask import Flask, request, jsonify

# Import custom defined database models
from models import *

# Create the Flask app and have it serve files from the 'static' directory on the root route ('/')
app = Flask(__name__, static_url_path='')

# Try to get the URL for our MongoDB server from the env variables (heroku)
mongodb_url = os.environ.get('MONGOLAB_URI', False)
if mongodb_url: connect('lingobingo', host=mongodb_url)
else: connect('lingobingo')

@app.route('/')
def home_serve():
    """Just serve index.html on the default route ('/')"""
    return app.send_static_file('index.html')

def shuffled(l):
    """Returns a copy of an array randomly shuffled (instead of in place)"""
    return sorted(l, key=lambda k: random.random())

@app.route('/start')
def start():
    """This function is called when the api endpoint '/start' is visited and it will generate a new game"""
    try:
        # Create the new game from the Game schema
        game = Game()
        # Fill in the player name from the passed url params
        game.player = request.args.get('player').strip()
        # Be sure to validate before population to let the user know if their wrong quickly
        game.validate()
        # Actually fill the game with snippets and data (for 10 questions)
        game.populate(10)
        # Validate again without saving
        game.validate()
        # Create a turns list to pass back to the client that shields the answers to the questions and generates a list
        # of possible answers
        turns = []
        # Shuffle the game snippets in place for mem efficiency
        random.shuffle(game.snippets)
        # Loop through each snippet...
        for snippet in game.snippets:
            # Start off the possibilities list with the correct answer
            poss = [snippet.language]
            # Append to it three random incorrect answers from the set of languages that exist in the game by getting
            # a list that excludes the correct answer, shuffling the list, and taking the first three items
            poss += shuffled([lang for lang in game.languages if lang != snippet.language])[:3]
            # Append to the turns list with a dict that has the snippets ID, its text, and its possible answers
            turns.append({
                'id': str(snippet.id),
                'snippet': snippet.text,
                'possibilities': shuffled(poss)
            })
        # Start the game
        game.start()
        # Save its DB record
        game.save()
        # Return the relevant info to the client
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
        # If a field failed to validate, it was likely the name. Inform the client of such.
        return jsonify(
            status='bad',
            error='A player name must be provided that consists of at least three alphanumeric characters and spaces: ' + str(e.message)
        )

@app.route('/submit', methods = ['POST'])
def submit():
    """The API enpoint that checks quiz answers"""
    # Get the form data and convert it to a dict
    data = dict(request.form.items())
    # Find the associated game by ID
    game = Game.objects(id=data.get('game'))[0]
    # Remove the game ID form data
    data.pop('game', None)
    # Count how many right answers there should be (10)
    total = len(game.snippets)
    # Have a variable ready to count the number of right answers
    right = 0
    # Loop through each of the games snippets
    for snippet in game.snippets:
        # Find the write snippet answer in the form data...
        if snippet.id in data and data.get(snippet.id) == snippet.language:
            # If the answer is correct, increment right
            right += 1
    # If all were right, set won to true
    won = (right == total)

    if won:
        # Mark the game as finished and save
        game.finish()
        game.save()
        # Return relevant data about the player's winning to the client
        return jsonify(won=True, score=game.score, player=game.player, rank=game.get_rank())
    else:
        # Tell the client how many the player got right out of the total since they lost
        return jsonify(won=False, total=total, right=right)

@app.route('/leaderboard')
def board():
    """The API endpoint that serves the rankings as a list of finsihed games (pre-sorted)"""
    # Retrieve a QuerySet iterator that only includes finished games with valid scores
    query = Game.rank_query()
    # Create a list to hold the games and their incremental rank
    ranked_games = []
    # Start at rank 1
    rank = 1
    for game in query:
        game.rank = rank
        ranked_games.append(game)
        # Add the game to the list and increment the rank
        rank += 1
    # Return the list of ranked games to the client to list in a table
    return jsonify(games=[{'id':str(game.id),'started':game.started,'finished':game.finished,'score':game.score,'player':game.player,'rank':game.rank} for game in ranked_games])


if __name__ == '__main__':
    # Get the port from env variables and default to 5000
    port = int(os.environ.get('PORT', 5000))
    # SHould we have debugging features enabled?
    debug = os.environ.get('APP_ENV', 'development') == 'development'
    # Start the server
    app.run(host='0.0.0.0', port=port, debug=debug)