'''
Brandon Eric Phillips
06 October 2014
Madhu
Project 1
Lingo Bingo
'''

import os
from flask import Flask
app = Flask(__name__, static_url_path='')

@app.route('/')
def home_serve():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("APP_ENV", "development") == "development"
    app.run(host='0.0.0.0', port=port, debug=debug)