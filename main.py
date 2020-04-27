#! /usr/bin/env python3
# # -*- coding: utf-8 -*-

import sys, os, random
from functools import cmp_to_key
import asyncio, websockets, ssl, pathlib
import json

class CoincheGame:
    def __init__(self):
        print('Starting new game!')
        self.players = []
        self.cards = [ "A", "7", "8", "9", "10", "J", "Q", "K" ]
        # self.cards = [ "A", "9" ]
        self.suits = [ "diamonds", "hearts", "spades", "clubs" ]
        self.deck = []
        self.played = {}
        self.table = [None, None, None, None]
        self.last = [None, None, None, None]
        self.teams = {1:[], 2:[]}
        self.picked_up = False
        self.spectators = []

        self.ngsafe = 4
    
    def request_chair(self, chair, uid):
        chairs = {0: False, 1: False, 2: False, 3: False, 4: False }
        for p in self.players:
            chairs[p['chair']] = True
        
        if not chairs[chair]:
            for p in self.players:
                if uid == p['uid']:
                    p['chair'] = chair
                    return True
        return False
    
    def count_chairs_available(self):
        res = 0
        for p in self.players:
            if p['chair'] == 0:
                res += 1
        return res
    
    def sort_cards(self, cards):
        def cmp_cards(c1, c2):
            vals = {"7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13, "A":14 }
            suits = {"diamonds":1, "spades":2, "hearts":3, "clubs":4 }
            if c1['suit'] == c2['suit']:
                return vals[c2['value']] - vals[c1['value']]
            else:
                return suits[c2['suit']] - suits[c1['suit']]

        cards.sort(key=cmp_to_key(cmp_cards))
        return cards
    
    def add_player(self, uid, ws, name):
        print('Add player')
        if len(self.players) < 4:
            self.players.append({'uid': uid, 'ws': ws, 'name': name, 'chair': 0})
            return True
        else:
            self.spectators.append({'uid': uid, 'ws': ws, 'name': name, 'chair': 0})
            return False
    
    async def change_name(self, uid, name):
        for p in self.players:
            if p['uid'] == uid:
                p['name'] = name
                await self.update_players()
     
    def nb_player_left(self):
        return 4 - len(self.players)
    
    async def remove_player(self, uid):
        in_spectator = False
        new_spectators = []
        for p in self.spectators:
            if p['uid'] != uid:
                new_spectators.append(p)
            else:
                in_spectator = True
        self.spectators = new_spectators
        if in_spectator:
            return

        print('Remove player')
        new_players = []
        for p in self.players:
            if p['uid'] != uid:
                new_players.append(p)
        self.players = new_players
        self.deck = []
        self.played = {}
        self.table = [None, None, None, None]
        self.last = [None, None, None, None]
        self.teams = {1:[], 2:[]}
        self.picked_up = False
        self.reset()
        await self.update_players()
    
    async def reset(self):
        self.ngsafe = 4

        for p in self.players + self.spectators:
            infos = {
                'type': 'reset'
            }
            await p['ws'].send(json.dumps(infos))

    async def start_game(self):
        self.ngsafe = 4

        print('Start game')
        if len(self.players) < 4:
            return

        self.deck = []
        self.table = [None, None, None, None]
        self.last = [None, None, None, None]
        self.teams = {1:[], 2:[]}
        self.picked_up = False
        for s in self.suits:
            for c in self.cards:
                card = { 'value': c, 'suit': s }
                self.deck.append(card)

        random.shuffle(self.deck)
        n = int(len(self.deck)/4)
        for k in range(len(self.players)):
            infos = {
                'type': 'cards',
                'cards': self.deck[k*n:(k+1)*n]
            }
            infos['cards'] = self.sort_cards(infos['cards'])
            await self.players[k]['ws'].send(json.dumps(infos))
        for p in self.spectators:
            infos = {
                'type': 'cards',
                'cards': []
            }
            await p['ws'].send(json.dumps(infos))
    
    def remove_card_from_deck(self, card):
        print('Remove card from deck')
        new_deck = []
        for c in self.deck:
            if not (c['value'] == card['value'] and c['suit'] == card['suit']):
                new_deck.append(c)
        self.deck = new_deck

    async def playing(self, uid, card, chair):
        print('Playing')
        self.picked_up = False
        self.remove_card_from_deck(card)
        if uid in self.played:
            self.deck.append(self.played[uid])
        self.played[uid] = card
        self.table[chair-1] = card
        for p in self.players:
            infos = {
                'type': 'table',
                'cards': self.table,
                'last': self.last,
                'chair': chair
            }
            await p['ws'].send(json.dumps(infos))
        for p in self.spectators:
            infos = {
                'type': 'table',
                'cards': self.table,
                'last': self.last,
                'chair': chair
            }
            await p['ws'].send(json.dumps(infos))

    async def update_players(self):
        players = []
        for p in self.players:
            players.append({'chair': p['chair'], 'name': p['name']})

        for p in self.players + self.spectators:
            infos = {
                'type': 'player',
                'lplayers': game.nb_player_left(),
                'lchairs': game.count_chairs_available(),
                'players': players,
                'cards': self.table,
                'last': self.last,

            }
            await p['ws'].send(json.dumps(infos))
    
    async def hand_done(self, team):
        print('Hand done')
        if self.picked_up:
            return
        self.picked_up = True
        self.teams[team] += self.table
        self.last = self.table
        self.table = [None, None, None, None]
        self.played = {}
        for p in self.players:
            infos = {
                'type': 'newtable',
                'cards': self.table,
                'last': self.last
            }
            await p['ws'].send(json.dumps(infos))
        for p in self.spectators:
            infos = {
                'type': 'newtable',
                'cards': self.table,
                'last': self.last
            }
            await p['ws'].send(json.dumps(infos))

        if len(self.deck) == 0:
            for p in self.players:
                infos = {
                    'type': 'final',
                    'team1': self.teams[1],
                    'team2': self.teams[2],
                    'der': team
                }
                await p['ws'].send(json.dumps(infos))
            for p in self.spectators:
                infos = {
                    'type': 'final',
                    'team1': self.teams[1],
                    'team2': self.teams[2],
                    'der': team
                }
                await p['ws'].send(json.dumps(infos))



game = CoincheGame()    

clients = {}
loop = asyncio.get_event_loop()
async def fail_connection(websocket):
    global clients
    print('failed connection')
    ip = websocket.remote_address[0]
    if ip in clients:
        del clients[ip]

async def message(websocket, path):
    global clients

    asyncio.ensure_future(fail_connection(websocket))

    uid = int(random.random()*10000000)
    try:
        while True:
            msg = await websocket.recv()
            event, val = msg.split('?')
            val = eval(val)
            if event == 'user':
                res = game.add_player(uid, websocket, val['name'])
                infos = {
                    'type': 'ack',
                    'playing': res,
                    'uid': uid,
                    'cards': game.table,
                    'last': game.last
                }
                await websocket.send(json.dumps(infos))

                if res:
                    await game.reset()
                await game.update_players()
            elif event == 'chair':
                if game.request_chair(val, uid):
                    infos = {
                        'type': 'yours',
                        'chair': val
                    }
                    await websocket.send(json.dumps(infos))
                await game.update_players()
                if game.count_chairs_available() == 0:
                    await game.start_game()
            elif event == 'newgame':
                game.ngsafe -= 1
                if game.nb_player_left() == 0 and game.ngsafe == 0:
                    await game.start_game()
            elif event == 'play':
                card = { 'value': val['value'], 'suit':  val['suit'] }
                await game.playing(uid, card, val['chair'])
            elif event == 'pickup':
                await game.hand_done(val)
            elif event == 'name':
                await game.change_name(uid, val['name'])

        

    finally:
        await game.remove_player(uid)
        print('Connection lost with client.')

# server = websockets.serve(message, "192.168.1.20", 8765, max_size=2**32)
server = websockets.serve(message, "", 8765, max_size=2**32)

loop.run_until_complete(server)
loop.run_forever()