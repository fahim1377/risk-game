from flask import Flask, request, jsonify, session, g, current_app
from flask_cors import CORS
import numpy as np
import json
import math
from game import Game
from flask_session import Session
from uuid import uuid4

app = Flask(__name__)
CORS(app, supports_credentials=True)

game = {}

app.secret_key = 'okdok'

@app.route('/newGame', methods=['POST'])
def startGame():
    print(request.get_json())
    req = request.get_json()
    game_mode = req['gameMode']
    players_num = req['playersNum']
    map = req['map']
    types = req['playerTypes']
    session['game_id'] = str(uuid4())
    game_id = session['game_id']
    print(game_id)
    global game 
    game[game_id] = Game(map=map,mode=game_mode,player_types=types,players_num=players_num)
    game[game_id].start()
    game_json = game[game_id].json()
    game_json['game_id']=game_id
    response = jsonify(game_json)
    return response

@app.route('/player/<id>', methods=['GET'])
def get_player(id):
    global game
    risk = game[session['game_id']]
    return jsonify(risk.players[int(id)].json())

@app.route('/territory/<name>', methods=['GET'])
def get_territory(name):
    global game
    risk = game[session['game_id']]
    return jsonify(next((x.json() for x in risk.territories if x.name == name), None))

@app.route('/player/territories/<id>', methods=['GET'])
def get_player_territories(id):
    global game
    risk = game[session['game_id']]
    res = {
        'territories':[t.json() for t in risk.players[int(id)].territories]
    }
    return jsonify(risk.players[int(id)].json())

@app.route('/troopsNum/<id>', methods=['GET'])
def get_new_troops(id):
    global game
    res = {"troops_num":game[id].players[game[id].player_turn].get_new_troops()}
    return jsonify(res)

@app.route('/troops/assign/<id>', methods=['POST'])
def assign_new_troops(id):
    req = request.get_json()
    game_id = req['gameID']
    troop_territory = req['troops']
    global game
    game[game_id].players[int(id)].assign_new_troops(game[game_id],troop_territory)
    game_json = game[game_id].json()
    response = jsonify(game_json)
    return response

@app.route('/attack',methods=['POST'])
def attack():
    global game
    print(request.get_json())
    req = request.get_json()
    game_id = req['gameID']
    attacker_id = req['attackerID']
    attackee_id = req['attackeeID']
    attacker_territory_name =  req['attackerTerritory']
    attackee_territory_name = req['attackeeTerritory']
    troops_num = req['troopsNum']
    if attackee_id is None:
        attackee_id = 0
    attacker_territory = game[game_id].get_territory(attacker_territory_name)
    attackee_territory = game[game_id].get_territory(attackee_territory_name)
    status,msg = game[game_id].players[int(attacker_id)].attack(game[game_id],
    troops_num,attacker_territory,game[game_id].players[int(attackee_id)],attackee_territory)
    game_json = game[game_id].json()
    game_json['attack'] ={"status":status,"msg":msg}
    response = jsonify(game_json)
    return response

@app.route('/attack/passive/<playerid>', methods=['PUT'])
def attack_passive(playerid):
    gameid = request.get_json()['gameID']
    global game
    status,msg = game[gameid].players[int(playerid)].attack_passive(game[gameid])
    game_json = game[gameid].json()
    game_json['attack'] ={"status":status,"msg":msg}
    response = jsonify(game_json)
    return response

@app.route('/attack/aggressive/<playerid>', methods=['PUT'])
def attack_aggressive(playerid):
    gameid = request.get_json()['gameID']
    global game
    attacks,place_msg = game[gameid].players[int(playerid)].attack_aggressive(game[gameid])
    game_json = game[gameid].json()
    game_json['attacks'] =[{"status":attack[0],"msg":attack[1],"ai_msg":attack[2]} for attack in attacks]
    game_json['troops_msg']=place_msg
    response = jsonify(game_json)
    return response

@app.route('/attack/pacifist/<playerid>', methods=['PUT'])
def attack_pacifist(playerid):
    gameid = request.get_json()['gameID']
    global game
    status,msg,ai_msg = game[gameid].players[int(playerid)].attack_pacifist(game[gameid])
    game_json = game[gameid].json()
    game_json['attack'] ={"status":status,"msg":msg,"ai_msg":ai_msg}
    response = jsonify(game_json)
    return response    

@app.route('/attack/agent/<playerid>', methods=['PUT'])
def get_move(playerid):
    gameid = request.get_json()['gameID']
    global game
    player = game[gameid].players[int(playerid)]
    if player.type ==7:
        attacks,place_msg = game[gameid].players[int(playerid)].get_minimax_move(game[gameid])
    else:
        attacks,place_msg = game[gameid].players[int(playerid)].get_move(game[gameid],1,2)
    game_json = game[gameid].json()
    game_json['attacks'] =[{"status":attack[0],"msg":attack[1],"ai_msg":attack[2]} for attack in attacks]
    game_json['troops_msg']=place_msg
    response = jsonify(game_json)
    return response  

@app.route('/pass/<id>', methods=['PUT'])
def pass_turn(id):
    req = request.get_json()
    game_id = req['gameID']
    global game
    game[game_id].players[int(id)].pass_turn(game[game_id])
    game_json = game[game_id].json()
    response = jsonify(game_json)
    return response

@app.route('/reset', methods=['PUT'])
def reset_game():
    req = request.get_json()
    game_id = req['gameID']
    global game
    game.pop(game_id,None)
    print("Game Reset")
    print(game)
    return jsonify({})

@app.route('/join/<id>', methods=['GET'])
def join_game(id):
    global game
    if id in game.keys():
        game_json = game[id].json()
        return jsonify(game_json)
    else: return jsonify(None)

if __name__ == '__main__':
    from chanceNode import load_dataset
    load_dataset()
    app.run(debug=True)
