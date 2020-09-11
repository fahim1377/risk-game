# RISK GAME

Risk board game webapp implemented in python with angular 6

## Requirements
- Python 3
- Flask
- Angular 6
- Primeng

## Playing Agents
AI Agents implemented are:
- A* Search 
- IDA* Search 
- Greedy Search 
- Minimax

Non-AI Agents implemented are:
- Human
- Passive (Makes no attacks) 
- Aggressive (Makes every attack possible)
- Pacifist (Makes just the one attack)

## Demo

![alt text](https://github.com/ZeyadZanaty/risk-game-ai/blob/master/test-2.gif?raw=true "Demo")

## Running

- Install python 3.6+, angular 6
- Install python requirements by running `pip install -r requirements.txt`
- cd into /server
- Run `python server.py`
- cd into /client/Risk
- Run `npm install`
- Run `ng s`
- go to `localhost:4200` in your browser and start playing

## Minimax AI
In this agent I am expanding decision tree according to chance in game until 3 level(
as there is limitation time on each step) and choose that one is best for agent by
bsr-heuristic,this agent can fail all agents that implemented before in this project
like A*,IDA*,Greedy and Minimax, you can see the main procedure of minimax agent
on chanceNode.py,but for other agent see node.py.
The non-minimax agent game-project is given from https://github.com/Galiold/risk-game-ai 
