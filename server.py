from flask import Flask
import logging
app = Flask('')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def main():
    return "Im Alive"

def keep_alive():
    app.run(host='0.0.0.0', port=8080)