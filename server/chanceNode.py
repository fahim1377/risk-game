import numpy as np
import copy, random
import json

sdict = None


def load_dataset():
    global sdict
    sdict = json.load(open('sdict.json'))


class chance_Node:
    def __init__(self, game, state, player, phase=0, parent=None, depth=0, path_cost=0, cost=0, prev_action=None,
                 stochastic=False):
        self.game = game
        self.state = copy.deepcopy(state)
        self.player = player
        self.parent = parent
        if self.parent is None:
            self.depth = depth
        else:
            self.depth = self.parent.depth + 1
        self.cost = cost
        self.path_cost = path_cost
        self.phase = phase
        if self.parent is None:
            self.stochastic = stochastic
        else:
            self.stochastic = self.parent.stochastic
        self.prev_action = prev_action
        self.moves = []
        self.children = []
        self.update_state()

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return "Node(%s)" % (self.state)

    def __eq__(self, other):
        if isinstance(other, chance_Node):
            return (self.state == other.state and self.phase == other.phase)
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.__repr__())

    def decrease_key(self, frontier):
        for n in frontier:
            if self.state == n.state and self.phase == n.phase and self.cost < n.cost:
                self = copy.deepcopy(n)
                break

    def get_reinforce(self, trts, sorted_trts):
        children = []
        new_troops = max(3, len(trts) // 3)
        for trt in sorted_trts:
            children.append(chance_Node(self.game, self.state, self.player, phase=1, parent=self,
                                        prev_action={'move_type': 'reinforce', 'territory': trt.name,
                                                     'troops': new_troops}))
        return children

    def get_attack(self, trts, sorted_trts):
        children = []
        for trt in sorted_trts:
            for other in trt.adjacent_territories:
                if other not in list(self.state[self.player.id].keys()):
                    troops = self.state[self.player.id][trt.name] - 1
                    if troops >= 1:
                        for i in range(1, 2):
                            attack_troops = troops // i
                            children.append(chance_Node(self.game, self.state, self.player, parent=self,
                                                        phase=1,
                                                        prev_action={'move_type': 'attack', 'attacking': trt.name,
                                                                     'troops': attack_troops, 'attacked': other,
                                                                     'attacked_player': self.get_trt_occupier(other)}))
        if self.parent and self.parent.prev_action and self.parent.prev_action[
            'move_type'] != 'reinforce' and self.player.type != 4:
            children.append(chance_Node(self.game, self.state, self.player, phase=0, parent=self,
                                        prev_action={'move_type': 'end_turn'}))
        return children

    def get_neighbors(self, reinforce_threshold, attack_threshold):
        children = []
        trts = []
        sorted_trts = []
        for territory in list(self.state[self.player.id].keys()):
            trts.append(territory)
        if self.phase == 0:
            trts.sort(key=lambda x: self.bsr(x), reverse=True)
            # sorted_trts = [self.game.get_territory(trt) for trt in trts if (self.bsr(trt) >= reinforce_threshold)]
            for trt in trts:
                if (self.bsr(trt) >= reinforce_threshold) and len(sorted_trts)<3:
                    sorted_trts.append(self.game.get_territory(trt))
            if len(trts) == 0:
                sorted_trts = trts
            elif len(sorted_trts) == 0:
                sorted_trts = [self.game.get_territory(trts[0])]
            children = self.get_reinforce(trts, sorted_trts)
        elif self.phase == 1:
            trts.sort(key=lambda x: self.bsr(x))
            sorted_trts = [self.game.get_territory(trt) for trt in trts if
                           self.bsr(trt) <= attack_threshold and self.state[self.player.id][trt] > 1]
            if len(sorted_trts) == 0:
                children.append(chance_Node(self.game, self.state, self.player, phase=0, parent=self,
                                            prev_action={'move_type': 'end_turn'}))
            else:
                if self.stochastic:
                    children = self.get_attack_with_prob(trts, sorted_trts)
                else:
                    children = self.get_attack(trts, sorted_trts)
        return children

    def get_trt_occupier(self, territory):
        for p, trts in self.state.items():
            for trt in trts.keys():
                if trt == territory:
                    return p

    def calculate_utility(self):
        self.utility = sum(
            [1 / self.bsr(trt) if self.bsr(trt) != 0 else 0 for trt in self.state[self.player.id].keys()]) + (
                           len(self.state[self.player.id].items()))
        # self.utility += sum([self.border_attackability(trt) for trt in self.state[self.player.id].keys()])/8
        if self.prev_action and self.prev_action['move_type'] == 'attack' and 'probability' in self.prev_action.keys():
            self.utility += self.prev_action['probability']/2

    def calculate_heuristic(self):
        self.heuristic = sum([self.bsr(trt) for trt in self.state[self.player.id].keys()]) - (
                    len(self.state[self.player.id].items()) - len(self.game.territories.items()))
        if self.prev_action and self.prev_action['move_type'] == 'attack' and 'probability' in self.prev_action.keys():
            self.heuristic -= self.prev_action['probability']
        if self.prev_action and self.prev_action['move_type'] == 'end_turn':
            if self.player.type in [4, 6]:
                self.heuristic += 3

    def calculate_cost(self):
        self.calculate_heuristic()
        if self.parent is None:
            self.cost = self.heuristic
        else:
            self.path_cost = self.parent.path_cost + 1
            self.cost = self.path_cost + self.heuristic
            if self.prev_action and self.prev_action['move_type'] == 'end_turn':
                self.cost += 3

    def update_state(self):
        previous_action = self.prev_action
        if previous_action == None:
            return
        elif previous_action['move_type'] == 'reinforce':
            self.state[self.player.id][previous_action['territory']] += previous_action['troops']
        elif previous_action['move_type'] == 'attack':
            if self.stochastic:
                self.attack_with_prob(previous_action)
            else:
                self.attack(previous_action)
        elif previous_action['move_type'] == 'end_turn':
            return

    # def bsr(self, trt): # fahim bsr
    #     get = getattr(self.game, 'get_territory')
    #     bsr = sum([(self.state[self.get_trt_occupier(territory)][territory]) ** 2 for territory in
    #                get(trt).adjacent_territories if self.get_trt_occupier(territory) != self.player.id])
    #     bsr = (bsr**(1/2)) / self.state[self.player.id][trt]
    #     return bsr

    def bsr(self, trt):
        get = getattr(self.game, 'get_territory')
        bsr = sum(
            [(self.state[self.get_trt_occupier(territory)][territory]) for territory in get(trt).adjacent_territories if
             self.get_trt_occupier(territory) != self.player.id])
        bsr = bsr / self.state[self.player.id][trt]
        return bsr

    def border_attackability(self, trt):
        result = 0
        get = getattr(self.game, 'get_territory')
        for territory in get(trt).adjacent_territories:
            if self.get_trt_occupier(territory) != self.player.id:
                if (self.state[self.player.id][trt] - 1 ) >= (self.state[self.get_trt_occupier(territory)][territory]):
                    result += 1
        print(f"{trt} attackability : {result}")
        return result

    def corrlation(self, trt):
        get = getattr(self.game, 'get_territory')
        enemy = sum(
            [1 for territory in get(trt).adjacent_territories if self.get_trt_occupier(territory) != self.player.id])
        me = sum(
            [1 for territory in get(trt).adjacent_territories if self.get_trt_occupier(territory) == self.player.id])
        if enemy == 0:
            return 5
        corr = me / enemy
        return corr

    def bsr(self, trt):
        get = getattr(self.game, 'get_territory')
        bsr = sum(
            [self.state[self.get_trt_occupier(territory)][territory] for territory in get(trt).adjacent_territories if
             self.get_trt_occupier(territory) != self.player.id])
        # prevv_action = self.prev_action
        # print(f"MYLOG: territory : { trt} ,won {prevv_action['won']} , lose {prevv_action['lose']} , attacking : {prevv_action['troops']} ")
        # print(f"MYLOG: territory : { trt} , troops : {self.state[self.player.id][trt]}")
        bsr = bsr / self.state[self.player.id][trt]
        return bsr

    def attack(self, previous_action):
        # attack logic
        attacking_troops = previous_action['troops']
        attacking_trt = previous_action['attacking']
        attacked_trt = previous_action['attacked']
        attacked_player = previous_action['attacked_player']
        # attacked_troops = self.state[attacked_player][attacked_trt]
        lost = 0
        attacking = copy.deepcopy(attacking_troops)
        while attacking_troops > 0:
            attacker_dice = []
            defender_dice = []
            random.seed()
            attacker_dice = [random.randint(1, 6) for _ in range(0, min(3, attacking_troops))]
            attacker_dice.sort(reverse=True)
            defender_dice = [random.randint(1, 6) for _ in range(0, min(3, attacking_troops))]
            defender_dice.sort(reverse=True)
            for i in range(0, min(3, attacking_troops)):
                if attacker_dice[i] > defender_dice[i] and attacked_trt not in self.state[self.player.id].keys():
                    if self.state[attacked_player][attacked_trt] > 0:
                        self.state[attacked_player][attacked_trt] -= 1
                    if self.state[attacked_player][attacked_trt] == 0:
                        self.state[self.player.id][attacked_trt] = attacking - lost
                        self.state[attacked_player].pop(attacked_trt)
                        break
                elif attacker_dice[i] <= defender_dice[i] and attacked_trt not in self.state[self.player.id].keys():
                    if self.state[self.player.id][attacking_trt] > 0:
                        self.state[self.player.id][attacking_trt] -= 1
                        lost += 1
            attacking_troops -= 3

    def get_attack_with_prob(self, trts, sorted_trts):
        children = []
        global sdict
        for trt in sorted_trts:
            for other in trt.adjacent_territories:  # defender trts
                if other not in list(self.state[self.player.id].keys()):
                    troops = self.state[self.player.id][trt.name] - 1  # num of attacking troops
                    if troops >= 1:
                        other_player = self.get_trt_occupier(other)
                        defend_troops = self.state[other_player][other]
                        if defend_troops >= troops:
                            attack_troops = troops
                        else:
                            attack_troops = defend_troops +1

                        # print(f"MYLOG: item count : {len(sdict[attack_troops][defend_troops].items())}")
                        for k, v in sdict[attack_troops][defend_troops].items():
                            if self.state[other_player][other] == 0:
                                children.append(chance_Node(self.game, self.state, self.player, parent=self,
                                                            phase=1,
                                                            prev_action={'move_type': 'attack', 'attacking': trt.name,
                                                                         'troops': attack_troops, 'attacked': other,
                                                                         'attacked_player': self.get_trt_occupier(
                                                                             other), 'won': attack_troops,
                                                                         'probability': 1}))
                                break
                            alive_attacker = int(k.split()[2])  # won
                            alive_other = int(k.split()[3])  # lose
                            if v > 70 and (defend_troops - alive_other) > 0:
                                children.append(chance_Node(self.game, self.state, self.player, parent=self,
                                                            phase=1,
                                                            prev_action={'move_type': 'attack', 'attacking': trt.name,
                                                                         'troops': attack_troops, 'attacked': other,
                                                                         'attacked_player': other_player,
                                                                         'won': alive_attacker, 'lose': alive_other,
                                                                         'probability': v / 1401}))
        if self.parent and self.parent.prev_action and self.parent.prev_action['move_type'] != 'reinforce':
            children.append(chance_Node(self.game, self.state, self.player, phase=0, parent=self,
                                        prev_action={'move_type': 'end_turn'}))
        return children

    def attack_with_prob(self, previous_action):
        # attack logic
        attacking_troops = previous_action['troops']
        attacking_trt = previous_action['attacking']
        attacked_trt = previous_action['attacked']
        attacked_player = previous_action['attacked_player']
        won = previous_action['won']
        lost = attacking_troops - won
        enemy_alive = previous_action['lose']
        enemy_lost = self.state[attacked_player][attacked_trt] - enemy_alive
        # print(f"MYLOG : won {won}  lost {lost} enemy alive {enemy_alive} attacking {attacking_trt} attacked {attacked_trt} troop: {attacking_troops} defend {self.state[attacked_player][attacked_trt]}")
        if won != 0:
            if self.state[attacked_player][attacked_trt] == 0:
                self.state[self.player.id][attacked_trt] = won
                self.state[attacked_player].pop(attacked_trt)
                self.state[self.player.id][attacking_trt] -= won
            elif enemy_alive == 0:
                self.state[self.player.id][attacked_trt] = won
                self.state[attacked_player].pop(attacked_trt)
                self.state[self.player.id][attacking_trt] -= attacking_troops
            else:  # none of players won
                self.state[self.player.id][attacking_trt] -= lost
                self.state[attacked_player][attacked_trt] -= enemy_lost

        else:
            self.state[self.player.id][attacking_trt] -= lost
            self.state[attacked_player][attacked_trt] -= enemy_lost

