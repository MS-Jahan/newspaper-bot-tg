from flask import Flask
from threading import Thread
import os

app = Flask('YoYo')

@app.route('/')
def main():
	return "<h1>Your Bot Is Alive!</h1>"

def run():
    try:
        app.run(host="0.0.0.0", port=int(os.environ['PORT']))
    except:
        app.run(host="0.0.0.0", port=int(8080))


def keep_alive():
    server = Thread(target=run)
    server.start()
