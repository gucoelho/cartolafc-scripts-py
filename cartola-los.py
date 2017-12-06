#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import unicodecsv as csv
from datetime import datetime


def try_request(url, headers=None, attempt=5):
    try:
        return requests.get(url, headers=headers)
    except:
        if attempt > 0:
            return try_request(url, headers, attempt-1)

# base urls
BASE_URL = 'https://api.cartolafc.globo.com/'
AUTH_URL = 'https://login.globo.com/api/authentication'

# endpoints
ROUNDS = 'rodadas'
LEAGUE = 'auth/liga/los-resenha-league'
ROUND_TEAM = 'time/slug/{}/{}'

# auth
email = ''
password = ''

payload = {'payload': {'email' : email, 'password': password,'serviceId':4728}}

token_response = requests.post(AUTH_URL, json=payload).json()

token = token_response["glbId"]

headers = {'X-GLB-Token': token}

league_teams = requests.get('{0}{1}'.format(BASE_URL, LEAGUE), headers=headers).json()

teams_slugs = []

for team in league_teams['times']:
    teams_slugs.append({
                         'slug': team['slug'],
                         'nome_jogador': team['nome_cartola'],
                         'nome_time': team['nome']
                       })

rounds_info = requests.get(BASE_URL + ROUNDS, headers=headers).json()

results = []

for round in rounds_info:
    month = datetime.strptime(round['fim'], '%Y-%m-%d %H:%M:%S').month
    for team in teams_slugs:
            team_round = try_request(
                 BASE_URL + ROUND_TEAM.format(team['slug'], round['rodada_id']),
                 headers=headers).json()
    
            points = team_round['pontos']
            
            results.append({
                 'rodada': round['rodada_id'],
                 'mês': month,
                 'slug': team['slug'],
                 'nome_time': team['nome_time'],
                 'nome_jogador': team['nome_jogador'],
                 'pontos': points
             })
    
            print round['rodada_id'], month, team, points

header = set({k for d in results for k in d.keys()})

with open('result.csv', 'wb') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()
    writer.writerows(results)
