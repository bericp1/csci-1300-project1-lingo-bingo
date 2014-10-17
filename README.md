# What is LingoBingo?

It's source is hosted [here](https://github.com/bericp1/lingo-bingo) on github.

[What's that!? A shortcut to the heroku-hosted game right at the top of the README for the lazy readers like me.](http://lingo-bingo.herokuapp.com/)

LingoBingo is a game that's actually not a whole lot like bingo, really... oh well. Anyway, you're given 10 questions
that you must answer correctly in as little time as possible. The less time you use, the higher the score you get. Each
question is a snippet of code pulled from a public gist from Github.com. The player must select for each snippet what
language he or she thinks its written in. The stream of public gists is essentially non-stop which means endless,
user-generated testing material. LingoBingo features a competitive leaderboard where users can track their progress
pseudo-anonymously.

# Scoring

You do not get a score at all if you can't get 10 out of 10 on any given quiz. When you do though, the server subtracts
the time you started from the time you began and that's your score. The lower the score, the higher the rank, like in
golf but much more interesting.

# Play Lingo Bingo w/o Installing Anything

LingoBingo is running pre-built on heroku. You can find it [here](http://lingo-bingo.herokuapp.com/). It's **highly**
recommended you play it this way since you'll be able to see a running leaderboard there of other people beside yourself.

# What's required to build/run LingoBingo

Essentially:

 - MongoDB server
 - Python3
 - The following modules for python
   - Flask
   - MongoEngine
   - Requests
   
The first two need to be installed by your system's package manager but the python dependencies are installed locally
in the venv folder. If you already have the first two deps installed, you can run the server by doing the following:

    $ cd /dir/where/you/extracted/me
    $ . ./venv/bin/activate
    $ ./venv/bin/python lingobingo.py

Or you could just install the pythnon deps listed above and just do

    $ python3 lingobingo

# Structure

All static files for the very minimal front end are found in the `static` directory. Screenshots can be found in the
`screenshots` directory.

# Screenshots

![Home](https://raw.githubusercontent.com/bericp1/lingo-bingo/master/screenshots/home.png)
![Loading](https://raw.githubusercontent.com/bericp1/lingo-bingo/master/screenshots/loading.png)
![Playing](https://raw.githubusercontent.com/bericp1/lingo-bingo/master/screenshots/playing.png)
![Right](https://raw.githubusercontent.com/bericp1/lingo-bingo/master/screenshots/right.png)
![Wrong](https://raw.githubusercontent.com/bericp1/lingo-bingo/master/screenshots/wrong.png)
![Leaderboard](https://raw.githubusercontent.com/bericp1/lingo-bingo/master/screenshots/leaderboard.png)

### P.S.!

This is a markdown file. You can view a nicely formatted version if you visit [the project on Github](https://github.com/bericp1/lingo-bingo).