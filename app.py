# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, render_template, request, session, jsonify, send_from_directory
from flask_cors import CORS
import json
import sys
import os
from eval import *

BLINDS = (5, 2)
DEFAULT_STACK = 500


# The condiut between the backend and a Mysql database
class DB():
    def __init__(config_name='init.ini'):
        config = configparser.ConfigParser()
        config.read(config_name)
        self.conn = pymysql.connect(**config['db'])

    def _eb(mod, dic):
        # Build statement of the form a = b, d = e, ...
        return mod.join(['%s = %s' % (k, v) for k, v in update_args.items()])
    def _update(table, select_args, update_args):
        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE %s SET %s WHERE %s" % (table,
                _eb(',', update_args), _eb(' and ', select_args)))
    def _select(table, select_args):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM %s WHERE %s" % (table, _eb(' and ', select_args)))
            return cursor
    def _insert(table, select_args):
        with self.conn.cursor() as cursor:
            keys, vals = zip(*select_args.items())
            cursor.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, ','.join(keys), ','.join(vals)))

    def _get_user(gname, uname):
        return _select('user', {'gname': gname, 'name': uname})

    def get_user(gname, uname):
        cur = _get_user(gname, uname)
        if cur.rowcount == 0:
            return None
        return cur.fetchone()
    def add_user(gname, uname):
        if _get_user(gname, uname).rowcount == 0:
            _insert('user', {'gname': gname, 'name': uname})
    def update_user(gname, uname, params):
        _update('user', {'gname': gname, 'name': uname}, params)
    def create_game(name):
        _insert('game', {'name': name})
    def exists_game(name):
        return _select('game', {'name': name}).rowcount != 0


# Maintains a game's state. Executes poker logic. Syncs game state with database
def Game():
    self __init__(gname, db):
        self.names = []
        #self.positions = {}
        self.db = db
        self.gname = gname
        self.ps = None
    def _get_current_position(self):
        self.ps.get_state()

    def _new_game(self, stacks, current_position):
        self.ps = Poker(stacks, self.names[current_position], BLINDS)
        
    def _export_to_db(self):

    def add_user(self, uname):
        self.names.append(uname)
        if len(self.stacks) >= 2 and self.ps is None:
            self._new_game([DEFAULT_STACK, DEFAULT_STACK])
        else:
            self._new_game(self.ps.get_state()[0]+[DEFAULT_STACK])

    def try_action(self, uname, atype):
        try:
            self.ps.step(atype) # TODO
        except Exception as e:
            print(e)
            return False
        if ps.get_state()[5] in (FOLDED, SHOWDOWN):
            self._new_game(self.ps.get_state()[0])

    def stand_up(self, uname):
        self.names.remove(uname)
        #upos = next(k for k, v in self.positions.iteritems() where v == uname)
        #del self.positions[upos]

    def get_state(self):
        return self.ps.get_state()



app = Flask(__name__)
CORS(app)

db = DB()
games = {}

# ======== Routing =========================================================== #
# -------- Logn ------------------------------------------------------------- #
@app.route('/api/create_game', methods=['GET'])
def create_game():
    gname = request.args.get("game")
    if db.exists_game(gname):
        return "Game already exists", 409
    db.create_game(gname)
    return "Done"

@app.route('/api/join_game', methods=['GET'])
def join_game():
    gname = request.args.get("gname")
    uname = request.args.get("uname")
    if not db.exists_game(gname):
        return "Game not found in db", 404

    db.add_user(gname, uname)
    if gname not in games:
        games[gname] = Game(gname, db)

    games[gname].add_user(uname)

    return "Done"

@app.route("/api/state", methods=['GET'])
def state():
    gname = request.args.get("gname")
    if gname not in games:
        return "No one in game", 404
    return jsonify(games[gname].get_state())

@app.route("/api/leaderboard", methods=['GET'])
def leaderboard():
    gname = request.args.get("gname")
    if gname not in games:
        return "No one in game", 404
    return jsonify(games[gname].get_leaderboard())

@app.route("/api/action", methods=['GET'])
def action():
    gname = request.args.get("gname")
    uname = request.args.get("uname")
    ast = request.args.get("action")

    atype = ast.upper() if ":" not in ast else (ast.split(":")[0].upper(), int(ast.split(":")[1]))

    if gname not in games:
        return "No one in game", 404
    success = games[gname].try_action(uname, atype)
    return "Done"

@app.route("/api/stand_up", methods=['GET'])
def stand_up():
    gname = request.args.get("gname")
    uname = request.args.get("uname")
    if gname not in games:
        return "No one in game", 404
    games[gname].stand_up(uname)
    return "Done"

@app.route('/', defaults={'path': ''})
@app.route('/<path>')
def send_js(path):
    if path == '':
        return send_from_directory('static', 'home.html')
    return send_from_directory('static', 'poker.html')


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, use_reloader=True)