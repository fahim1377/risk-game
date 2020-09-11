import random
import numpy as np
import json

a = 100
b = 100

# def attack(attacker,attacked):
#      #attack logic
#     attacking_troops = attacker
#     # attacked_troops = self.state[attacked_player][attacked_trt]
#     lost = 0
#     finish = False
#     while attacking_troops >0:
#         attacker_dice = []
#         defender_dice = []
#         random.seed()
#         attacker_dice=[random.randint(1, 6) for _ in range(0,min(3,attacking_troops))]
#         attacker_dice.sort(reverse=True)
#         defender_dice=[random.randint(1, 6) for _ in range(0,min(3,attacking_troops))]
#         defender_dice.sort(reverse=True)
#         for i in range(0,min(3,attacking_troops)):
#             if attacker_dice[i] > defender_dice[i] and not finish:
#                 if attacked>0:
#                     attacked-=1
#                 if attacked == 0:
#                     # attacked = temp-lost
#                     finish = True
#                     break
#             elif attacker_dice[i]<= defender_dice[i]  and not finish:
#                 if attacker>0:
#                     attacker-=1
#                     lost+=1
#         attacking_troops-=3
#         if finish:
#             break
    
#     return attacker,attacked


# sdict = []
# for i in range(0,a):
#         sdict.append([])
#         for j in range(0,b):
#             sdict[i].append(dict())

# for k in range(0,10000):
#     print(k)
#     for i in range(1,a):

#         for j in range(1,b):
#             attacker,attacked = attack(i,j)
#             keystring = str(i)+" "+str(j)+" "+str(attacker)+" "+str(attacked)
#             if keystring in sdict[i][j]:
#                 sdict[i][j][keystring] += 1
#             else:
#                 sdict[i][j][keystring] = 1 
#     if k % 100 == 0:
#         json.dump(sdict,open('sdict.json','w'))




# json.dump(sdict,open('sdict.json','w'))

sdict = json.load(open('sdict.json'))

for i in range(1,a):

        for j in range(1,b):
                
            for k,v in sdict[i][j].items():
                print(str(k)+" "+str(v))
    






