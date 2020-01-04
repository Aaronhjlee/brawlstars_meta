import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize

from API_key import *
import requests as r


'''
Get the player information
'''

class BSdata():

    def __init__(self, country_code, headers):
        self.country_code = country_code
        self.headers = headers

    def top_200(self):
        data = r.get('https://api.brawlstars.com/v1/rankings/' + self.country_code +'/players', headers=self.headers).json()
        player_id = []
        names = []
        for i in data['items']:
            player_id.append(i['tag'])
            names.append(i['name'])
        return player_id, names

    def gather_account_info(self):
        player_id, names = self.top_200()
        clean_id = []
        for i in player_id:
            clean_id.append(i[1:])
            
        account_info = []
        for i in clean_id:
            temp = (r.get('https://api.brawlstars.com/v1/players/%23' + i, headers=self.headers).json())
            account_info.append(temp)
        return account_info

    def brawler_names(self):
        data = r.get('https://api.brawlstars.com/v1/brawlers', headers=headers).json()
        brawler_names = []
        for i in data['items']:
            brawler_names.append(i['name'])
        return brawler_names

    def top_players(self):    
        account_info = self.gather_account_info()
        trophy_200 = []
        for i in account_info:
            trophy = []
            for j in i['brawlers']:
                trophy.append(j['trophies'])
            trophy_200.append(trophy)
        return trophy_200

    def makeDataframe(self):
        player_id, names = self.top_200()
        brawler_names = self.brawler_names()
        trophy_200 = self.top_players()
        
        df = pd.DataFrame(names, columns=['name'])
        df['id'] = player_id
        df2 = pd.DataFrame(data=trophy_200, columns=brawler_names)
        df = pd.concat([df, df2], axis=1)
        return df

'''
plotting character breakdown
'''

def plot_avg_trophies(df):
    avg_trophies = df.describe().transpose()[['mean']].reset_index().sort_values('mean', ascending=False)

    plt.figure(figsize=(16,8))
    plt.title('Average Trophies per Character', fontsize=30)
    plt.xlabel('Brawlers', fontsize=20)
    plt.ylabel('Brawlers', fontsize=20)
    
    avg = avg_trophies.mean().values[0]
    mask1 = avg_trophies['mean'] < avg
    mask2 = avg_trophies['mean'] >= avg

    plt.bar(avg_trophies['index'][mask2], avg_trophies['mean'][mask2], color='green')
    plt.bar(avg_trophies['index'][mask1], avg_trophies['mean'][mask1], color='red')
    
    plt.ylim((550, 850))
    plt.xticks(fontsize=14, rotation=90)
    plt.yticks(fontsize=14)
    
    plt.plot(avg_trophies['index'], [avg_trophies.mean()]*(len(avg_trophies['index'])), label='Mean={}'.format(round(avg,2)), linestyle='--')
    plt.legend(fontsize=20)


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
    country_code = 'global'
    
    BS = BSdata(country_code, headers)
    df = BS.makeDataframe()


# !curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$self.token"" 'https://api.brawlstars.com/v1/rankings/'$self.country_code'/players'
# !curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$token"" 'https://api.brawlstars.com/v1/players/%23'$i''