'''
Brandon Eric Phillips
06 October 2014
Madhu
Project 1
Lingo Bingo
'''

import os, sys
from flask import Flask
from mongoengine import *

app = Flask(__name__, static_url_path='')

mongodb_url = os.environ.get('MONGOLAB_URI', False)
if mongodb_url: connect('lingobingo', host=mongodb_url)
else: connect('lingobingo')

class TestDoc(DynamicDocument): pass

testDoc = TestDoc()
testDoc.testString = 'test'
testDoc.testInt = 1
testDoc.testFloat = 1.1
testDoc.save()

@app.route('/')
def home_serve():
    return app.send_static_file('index.html')

@app.route('/test')
def test():
    return str(TestDoc.objects().count())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('APP_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)