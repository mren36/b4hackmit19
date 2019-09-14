# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, render_template, request, session, jsonify, send_from_directory
from flask_cors import CORS
import json
import sys
import os
from eval import *

app = Flask(__name__)
CORS(app)

started = False
players = []
laststate = None
ps = None
showdown = {}

STARTINGSTACK = 500
BLINDS = (5, 2)

def newgame():
    global laststate, ps, players, showdown
    showdown = {} if laststate is None or laststate[5] != SHOWDOWN else laststate[1:3]
    players.reverse()
    plnew = {p:STARTINGSTACK for p in players} if laststate is None else laststate[0]
    ps = Poker(plnew, players[0], BLINDS)
    laststate = ps.get_state()

# ======== Routing =========================================================== #
# -------- Logn ------------------------------------------------------------- #
@app.route('/api/start', methods=['GET'])
def start():
    global started
    name = request.args.get("name")
    if name not in players:
        if len(players) >= 2:
            return jsonify({'full': True, 'info': players})
        players.append(name)
    print(started)
    if len(players) == 2:
        if not started:
            newgame()
        started = True
        return jsonify({'ready': True})
    return jsonify({'ready': False})

@app.route("/api/state", methods=['GET'])
def state():
    if started == False:
        return jsonify({'start': False})
    new_state = list(laststate)
    new_state[1] = laststate[1][request.args.get("name")]
    new_state.append(showdown)
    new_state = tuple(new_state)
    return jsonify(new_state)

@app.route("/api/action", methods=['GET'])
def action():
    global laststate, ps
    if laststate is None:
        return jsonify({'success': False}) 
    # Perform action
    ast = request.args.get("action")
    atype = ast.upper() if ":" not in ast else (ast.split(":")[0].upper(), int(ast.split(":")[1]))

    if laststate[4] != request.args.get("name"):
        return jsonify({'success': False})

    try:
        ps.step(atype) # TODO
    except Exception as e:
        print(e)
        return jsonify({'success': False})
    laststate = ps.get_state()
    print(laststate)
    if laststate[5] in (FOLDED, SHOWDOWN):
        print('DONE')
        newgame()
    return jsonify({'success': True})


@app.route("/api/logout", methods=['GET'])
def logout():
    started = False
    players = []
    laststate = None

    return jsonify({})

@app.route('/', defaults={'path': ''})
@app.route('/<path>')
def send_js(path):
    if path == '':
        return send_from_directory('static', 'home.html')
    return send_from_directory('static', 'poker.html')


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, use_reloader=True)
