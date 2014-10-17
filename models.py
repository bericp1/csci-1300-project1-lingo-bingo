__author__ = 'bericp1'

# Import libs
from mongoengine import *
import requests, re, time
from uuid import uuid4 as uuid

# A schema for snippets of code (github gists)
class Snippet(EmbeddedDocument):
    # A uuid
    id = StringField(required=True)
    # The gists file's text
    text = StringField(required=True)
    # The language the file is in
    language = StringField(required=True)
    # How to convert to string?
    def __str__(self):
        return 'Snippet in ' + str(self.language)

# A class that does all of the github-facing interaction to ensure we get reliable, language-unique, not-to-big, not-
# to-small gist snippets
class SnippetStack:
    # Who are we talking to?
    ENDPOINT = "https://api.github.com/gists/public"
    # TODO Make the max/min_size configurable
    # Max.min size in bytes
    MAX_SIZE = 7500
    MIN_SIZE = 250
    # Max/min number of lines
    MIN_LINES = 10
    MAX_LINES = 80
    def __init__(self, size, batch_size=500):
        """Init some variables and kick off the filling process"""
        self.size = size
        self.batch_size = batch_size
        self.next_url = False
        self.refresh()
    def refresh(self, reset_url=False):
        """kick off the filling process after a quick reset"""
        self.stack = []
        self.languages = []
        if reset_url: self.next_url = False
        self.fill()
    def make_next_request(self):
        """Make the next request eiher to the next_url or to the original endpoint if that's not set"""
        if self.next_url: return requests.get(self.next_url)
        else: return requests.get(SnippetStack.ENDPOINT, params={'per_page':self.batch_size})
    def parse_links(self, response):
        """Github returns in its responses a Link header that gives us info on what the next URL we should hit up is
        so we need to store this ans use it when possible to ensure consistency with the API"""
        # Split the Link header accross commas
        links = response.headers['Link'].split(',')
        # Reset next_url in case we can't find a "next" link
        self.next_url = False
        # Begin looping through the links
        for link in links:
            try:
                # Set the next link to the URL if found using regex in the Github defined format
                self.next_url = re.search('^\<(.+?)\>; rel="next"', link.strip()).group(1)
                break
            except AttributeError: pass # Otherwise do nothing
    def checkAndParse(self, file):
        """Will take in a file meta object from the gist response and run some checks on it to see if its a good
        snippet and will also retrieve it's contents"""
        # Fail the test if...
        if (
            file['language'] in self.languages or       # There is already a snippet with that language in this stack
            file['language'] == None or                 # There is not a language in the first place
            file['size'] > SnippetStack.MAX_SIZE or     # The file is larger than MAX_SIZE
            file['size'] < SnippetStack.MIN_SIZE        # or smaller than MIN_SIZE
        ):
            return False
        # Get and set the file contents from github as a string on the file object
        file['contents'] = requests.get(file['raw_url']).text
        # Count the number of new lines in the file
        line_count = sum(1 for line in file['contents'].split('\n') if line.strip()!='')
        # Only count as valid if line count is between MIN_LINES and MAX_LINES
        return line_count >= SnippetStack.MIN_LINES and line_count <= SnippetStack.MAX_LINES
    def fill(self):
        """Will actually loop through the pages of github's public gists to fill this stack"""
        if len(self.stack) >= self.size:
            # Bail out of this recursive function if the stack is full
            return self.stack
        # Make the appropriate request
        response = self.make_next_request()
        # Through an error if not 200 OK
        if response.status_code is not 200: raise SnippetStack.ApiError(response)
        # Do the link parsing as discussed earlier
        self.parse_links(response)
        # Parse the result of the API call
        data = response.json()
        # Loop through the list of gists
        for gist in data:
            # Loop through each gist's files
            for file in gist['files'].values():
                # Check and parse as described earlier...
                if self.checkAndParse(file):
                    # Add files language to language list for this stack
                    self.languages.append(file['language'])
                    # Create the new snippet and set its text and language apporpriately from the file
                    snippet = Snippet()
                    snippet.text = file['contents']
                    snippet.language = file['language']
                    # Generate a UUID for it since embedded documents don't get those by default
                    snippet.id = str(uuid())
                    # Add to the stack
                    self.stack.append(snippet)
                    # Bail out if full
                    if len(self.stack) == self.size: return self.stack
        # Call this same function again since the stack isn't yet full
        return self.fill()

    class ApiError(Exception):
        """A special exception for API errors"""
        def __init__(self, response):
            message = 'There was an error interfacing with github API.'
            try:
                message += ' Github message: ' + response.json().message
            except: pass
            super(Exception, self).__init__(message)
            self.response = response

def current_timestamp():
    """Get the current timestamp as JS would understand it (in milliseconds as an int)"""
    return int(round(time.time() * 1000))

class Game(Document):
    """The schema that defines a Game"""
    # Player Name
    player = StringField(required=True, min_length=3, max_length=255, regex='^[A-Za-z0-9 ]+$')
    # Timestamp when created
    created = IntField(required=True, default=current_timestamp)
    # Timestamp when filled with snippets
    populated = IntField(required=True, default=-1)
    # Timestamp when started
    started = IntField(required=True, default=-1)
    # Timestamp when finished
    finished = IntField(required=True, default=-1)
    # The score of the game
    score = IntField(required=True, default=-1)
    # The list of snippets (as a list of embedded documents since Snippet is an embedded document)
    snippets = ListField(EmbeddedDocumentField(Snippet))
    # THe list of languages used in this game
    languages = ListField(StringField())

    def __init__(self, count=20, auto_populate=False, *args, **values):
        super().__init__(*args, **values)
        if auto_populate: self.populate(count)

    def populate(self, count):
        """Use our SnippetStack to get a certain number of snippets and store them and their languages"""
        stack = SnippetStack(count)
        self.snippets = stack.stack
        self.languages = stack.languages
        # Create the populated timestamp
        self.populated = current_timestamp()

    def start(self):
        # Create the started timestamp indicating the game has started
        self.started = current_timestamp()

    def finish(self):
        # Create the finished timestamp to indicate the game has ended
        self.finished = current_timestamp()
        # Calcualte and set the score
        self.score = self.elapsed()

    def elapsed(self):
        """Score is calculated simply by differencing the finished and (started, populated, or created) timestamps
        (whichever comes first)"""
        if int(self.started) != -1:
            return current_timestamp() - int(self.started)
        elif int(self.populated) != -1:
            return current_timestamp() - int(self.populated)
        else:
            return current_timestamp() - int(self.created)
    @classmethod
    def rank_query(cls):
        """Returns a queryset that includes only games with valid scores and are completed and then sorts it by the score"""
        return cls.objects(score__gte=0).order_by('score')
    def get_rank(self):
        """Cheap and crappy way to get the current rank of this game"""
        # Get the ranking query defined above
        query = Game.rank_query()
        # Set the rank counter to 1
        rank = 1
        # Loop through each game in the databse in order of score/rank
        for game in query:
            if game.id == self.id:
                # If this is the current game, break to return the rank counter's current value
                break
            else:
                # Increment the rank if this game was not the active game
                rank += 1
        return rank