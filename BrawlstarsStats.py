import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize

from API_key import token


# !curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$token"" 'https://api.brawlstars.com/v1/players/%23'$player_id''

'''
Get the player information
'''

def top_200(country_code):
    rank_raw = curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$token"" 'https://api.brawlstars.com/v1/rankings/'$country_code'/players'
    country = json.loads(rank_raw[0] + rank_raw[1])
    player_id = []
    names = []
    for i in country['items']:
        player_id.append(i['tag'])
        names.append(i['name'])
    return player_id, names

def gather_account_info(player_id):
    clean_id = []
    for i in player_id:
        clean_id.append(i[1:])

    account_info = []
    for i in clean_id:
        temp = curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$token"" 'https://api.brawlstars.com/v1/players/%23'$i''
        account_info.append(json.loads(temp[1]))
    return account_info

def brawler_names():    
    brawler_names = []
    for i in account_info[0]['brawlers']:
        brawler_names.append(i['name'])
    return brawler_names

def top_players():    
    trophy_200 = []
    for i in account_info:
        trophy = []
        for j in i['brawlers']:
            trophy.append(j['trophies'])
        trophy_200.append(trophy)
    return trophy_200

def makeDataframe():
    df = pd.DataFrame(names, columns=['name'])
    df['id'] = player_id
    df2 = pd.DataFrame(data=trophy_200, columns=brawler_names)
    df = pd.concat([df, df2], axis=1)
    return df



'''
Find win percentage per gamemode for a player
'''

def winrateTotal(log):
    count = 0
    for i in log['items']:
        if i['battle']['mode'] != 'duoShowdown':
            if i['battle']['trophyChange'] > 0:
                count += 1
        elif i['battle']['rank'] != 3:
            if i['battle']['trophyChange'] > 0:
                count += 1
    return count/25

def winrateGG(log):
    wins = 0
    count = 0
    for i in log['items']:
        if i['battle']['mode'] == 'gemGrab':
            if i['battle']['trophyChange'] > 0:
                wins += 1
        else:
            count += 1
    return wins / (wins+count)

def winrateBB(log):
    wins = 0
    count = 0
    for i in log['items']:
        if i['battle']['mode'] == 'brawlBall':
            if i['battle']['trophyChange'] > 0:
                wins += 1
            else:
                count += 1
    return wins/(wins+count)


if __name__ == "__main__":
    country_code = 'US'
    
    player_id, names = top_200(country_code)
    account_info = gather_account_info(player_id)
    brawler_names = brawler_names()
    trophy_200 = top_players()
    df = makeDataframe()