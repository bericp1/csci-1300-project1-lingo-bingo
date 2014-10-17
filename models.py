__author__ = 'bericp1'

from mongoengine import *
import requests, re, time
from uuid import uuid4 as uuid

class Snippet(EmbeddedDocument):
    id = StringField(required=True)
    text = StringField(required=True)
    language = StringField(required=True)
    def __str__(self):
        return 'Snippet in ' + str(self.language)

class SnippetStack:
    ENDPOINT = "https://api.github.com/gists/public"
    # TODO Make the max/min_size configurable
    MAX_SIZE = 7500
    MIN_SIZE = 250
    MIN_LINES = 10
    MAX_LINES = 80
    def __init__(self, size, batch_size=500):
        self.size = size
        self.batch_size = batch_size
        self.next_url = False
        self.refresh()
    def refresh(self, reset_url=False):
        self.stack = []
        self.languages = []
        if reset_url: self.next_url = False
        self.fill()
    def make_next_request(self):
        if self.next_url: return requests.get(self.next_url)
        else: return requests.get(SnippetStack.ENDPOINT, params={'per_page':self.batch_size})
    def parse_links(self, response):
        links = response.headers['Link'].split(',')
        self.next_url = False
        for link in links:
            try:
                self.next_url = re.search('^\<(.+?)\>; rel="next"', link.strip()).group(1)
                break
            except AttributeError: pass
    def checkAndParse(self, file):
        if (
            file['language'] in self.languages or
            file['language'] == None or
            file['size'] > SnippetStack.MAX_SIZE or
            file['size'] < SnippetStack.MIN_SIZE
        ):
            return False
        file['contents'] = requests.get(file['raw_url']).text
        line_count = sum(1 for line in file['contents'].split('\n') if line.strip()!='')
        return line_count >= SnippetStack.MIN_LINES and line_count <= SnippetStack.MAX_LINES
    def fill(self):
        if len(self.stack) >= self.size:
            return self.stack
        response = self.make_next_request()
        if response.status_code is not 200: raise SnippetStack.ApiError(response)
        self.parse_links(response)
        data = response.json()
        for gist in data:
            for file in gist['files'].values():
                if self.checkAndParse(file):
                    self.languages.append(file['language'])
                    snippet = Snippet()
                    snippet.text = file['contents']
                    snippet.language = file['language']
                    snippet.id = str(uuid())
                    self.stack.append(snippet)
                    if len(self.stack) == self.size: return self.stack
        return self.fill()

    class ApiError(Exception):
        def __init__(self, response):
            message = 'There was an error interfacing with github API.'
            try:
                message += ' Github message: ' + response.json().message
            except: pass
            super(Exception, self).__init__(message)
            self.response = response

def current_timestamp():
    return int(round(time.time() * 1000))

class Game(Document):
    player = StringField(required=True, min_length=3, max_length=255, regex='^[A-Za-z0-9 ]+$')
    created = IntField(required=True, default=current_timestamp)
    populated = IntField(required=True, default=-1)
    started = IntField(required=True, default=-1)
    finished = IntField(required=True, default=-1)
    score = IntField(required=True, default=-1)
    snippets = ListField(EmbeddedDocumentField(Snippet))
    languages = ListField(StringField())

    def __init__(self, count=20, auto_populate=False, *args, **values):
        super().__init__(*args, **values)
        if auto_populate: self.populate(count)

    def populate(self, count):
        stack = SnippetStack(count)
        self.snippets = stack.stack
        self.languages = stack.languages
        self.populated = current_timestamp()

    def start(self):
        self.started = current_timestamp()

    def finish(self):
        self.finished = current_timestamp()
        self.score = self.elapsed()

    def elapsed(self):
        if int(self.started) != -1:
            return current_timestamp() - int(self.started)
        elif int(self.populated) != -1:
            return current_timestamp() - int(self.populated)
        else:
            return current_timestamp() - int(self.created)
    @classmethod
    def rank_query(cls):
        return cls.objects(score__gte=0).order_by('score')
    def get_rank(self):
        query = Game.rank_query()
        rank = 1
        for game in query:
            if game.id == self.id:
                break
            else:
                rank += 1
        return rank