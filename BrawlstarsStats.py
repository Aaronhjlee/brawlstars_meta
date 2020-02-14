import pandas as pd
import numpy as np
import json
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests as r

from API_key import *


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
            player_id.append(i['tag'][1:])
            names.append(i['name'])
        return player_id, names
        
    def make_bl_data(self):
        player_id, names = self.top_200()
        battle_log_data = []
        for p in player_id:
            battle_log_data.append(r.get('https://api.brawlstars.com/v1/players/%23' + p + '/battlelog', headers=self.headers).json())
            if len(battle_log_data) % 50 == 0:
                print ('{} battle logs recorded.'.format(len(battle_log_data)))
        return battle_log_data

    def gather_account_info(self):
        player_id, names = self.top_200()  
        account_info = []
        for i in player_id:
            temp = r.get('https://api.brawlstars.com/v1/players/%23' + i, headers=self.headers).json()
            account_info.append(temp)
            if len(account_info) % 50 == 0:
                print ('{} account information recorded.'.format(len(account_info)))
        return account_info

    def brawler_names(self):
        data = r.get('https://api.brawlstars.com/v1/brawlers', headers=headers).json()
        brawler_names = []
        for i in data['items']:
            brawler_names.append(i['name'])
        return brawler_names

    def top_trophies(self):    
        account_info = self.gather_account_info()
        trophy_200 = []
        for i in account_info:
            trophy = []
            for j in i['brawlers']:
                trophy.append(j['trophies'])
            trophy_200.append(trophy)
        return trophy_200

    def makeDataframe(self):
        print ('Making player IDs...')
        player_id, names = self.top_200()
        print ('...complete!')
        print ('Making brawler names...')
        brawler_names = self.brawler_names()
        print ('...complete!')
        print ('Gathering player info...')
        trophy_200 = self.top_trophies()
        print ('...complete!')
        print ('Making battle log data...')
        battle_log_data = self.make_bl_data()
        print ('...complete!')
        
        df = pd.DataFrame(names, columns=['name'])
        df['id'] = player_id
        df2 = pd.DataFrame(data=trophy_200, columns=brawler_names)
        df = pd.concat([df, df2], axis=1)
        return df, player_id, battle_log_data


'''
battle log DATA
'''

class BSbattlelog():
    
    def __init__(self, player_id, data):
        self.player_id = player_id
        self.data = data

    def usage_3v3(self):
        GG_wins, GG_loss, BB_wins, BB_loss, H_wins, H_loss, B_wins, B_loss, S_wins, S_loss = [], [], [], [], [], [], [], [], [], []
        for l in zip(self.data, self.player_id):
            for i in l[0]['items']:
                if 'starPlayer' in i['battle']:
                    for j in i['battle']['teams']:
                        for k in j:
                            if l[1] in k['tag']:
                                if i['battle']['result'] == 'victory': 
                                    if i['event']['mode'] == 'gemGrab':
                                        GG_wins.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'brawlBall':
                                        BB_wins.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'heist':
                                        H_wins.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'bounty':
                                        B_wins.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'siege':
                                        S_wins.append(k['brawler']['name'])
                                elif i['battle']['result'] == 'defeat':
                                    if i['event']['mode'] == 'gemGrab':
                                        GG_loss.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'brawlBall':
                                        BB_loss.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'heist':
                                        H_loss.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'bounty':
                                        B_loss.append(k['brawler']['name'])
                                    elif i['event']['mode'] == 'siege':
                                        S_loss.append(k['brawler']['name'])
        return GG_wins, GG_loss, BB_wins, BB_loss, H_wins, H_loss, B_wins, B_loss, S_wins, S_loss  

    def usage_solo(self):
        SS_wins, SS_loss, DS_wins, DS_loss = [], [], [], []
        for l in zip(self.data, self.player_id):
            for i in l[0]['items']:
                if 'starPlayer' not in i['battle']:
                    if i['event']['mode'] != 'duoShowdown' and i['event']['mode'] != 'roboRumble' and i['event']['mode'] != 'bigGame' and i['event']['mode'] != 'bossFight':
                        for j in i['battle']['players']:
                            if l[1] in j['tag']:
                                if i['battle']['rank'] < 5: 
                                    if i['event']['mode'] == 'soloShowdown':
                                        SS_wins.append(j['brawler']['name'])
                                    else:
                                        pass
                                else:
                                    if i['event']['mode'] == 'soloShowdown':
                                        SS_loss.append(j['brawler']['name'])
                                    else:
                                        pass
                    elif i['event']['mode'] == 'duoShowdown':
                        for j in i['battle']['teams']:
                            for k in j:
                                if l[1] in k['tag']:
                                    if i['battle']['rank'] < 3:
                                        DS_wins.append(k['brawler']['name'])
                                    else:
                                        DS_loss.append(k['brawler']['name'])
        return SS_wins, SS_loss, DS_wins, DS_loss

    def makeDataFrame_usage_3v3(self, solo=False):
        if solo == False:
            GG_wins, GG_loss, BB_wins, BB_loss, H_wins, H_loss, B_wins, B_loss, S_wins, S_loss = self.usage_3v3()
            games = [GG_wins, GG_loss, BB_wins, BB_loss, H_wins, H_loss, B_wins, B_loss, S_wins, S_loss]
            names = ['GemGrab', 'BrawlBall', 'Heist', 'Bounty', 'Siege']
        else:
            SS_wins, SS_loss, DS_wins, DS_loss = self.usage_solo()
            games = [SS_wins, SS_loss, DS_wins, DS_loss]
            names = ['SoloShowdown', 'DuoShowdown']
        k = []
        for i in range(0,len(games), 2):
            if games[i] != [] or games[i+1] != []:
                d = Counter(games[i])
                f = Counter(games[i+1])
                df = pd.DataFrame.from_dict(d, orient='index').reset_index()
                df.rename(columns={'index': 'brawlers', 0: 'wins'}, inplace=True)
                df['loss'] = df['brawlers'].map(f)
                df['total'] = df['wins'] + df['loss']
                df['winrate'] = round(df['wins']*100 / df['total'], 2)
                df['mode'] = [names[i//2]]*len(df)
                k.append(df)
            else:
                k.append('No {} games recorded'.format(names[i//2]))
                print ('No {} games recorded'.format(names[i//2]))
        df = pd.DataFrame()
        for i in k:
            if 'No' not in i:
                df = df.append(i)
        return df


'''
plotting DATA
'''

class BSplot():

    def __init__(self):
        pass
        
    def plot_avg_trophies(self, df, df2, mode='global'):
        df_group = df2.groupby('brawlers').sum()
        df_group['winrate'] = round(df_group['wins']*100 / df_group['total'], 2)
        df_group.reset_index(inplace=True)
        
        avg_trophies = df.describe().transpose()[['mean']].reset_index().sort_values('mean', ascending=False)
        avg_trophies = avg_trophies.merge(df_group, left_on='index', right_on='brawlers').drop('brawlers', axis=1)
        fig = px.bar(data_frame=avg_trophies, x='index', y='mean', hover_data=['winrate'], color='winrate') #, range_y=[700,900])
        fig.update_layout(title={'text': 'Average Trophies per Brawlers ({})'.format(mode), 'y': 0.90, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
        fig.show()

    def plot_brawler_usage(self, df, mode='global', graph_type='pie'):
        if mode != 'global':
            df = df[df['mode']==mode]
        else:
            df = df.groupby('brawlers').sum()
            df['winrate'] = round(df['wins']*100 / df['total'], 2)
            df.reset_index(inplace=True)
        if graph_type == 'pie':
            fig = px.pie(df, values='total', names='brawlers', hover_data=['winrate'])
            fig.update_layout(title={'text': 'Brawler Usage Rate in {}'.format(mode), 'y': .95, 'x':0.42, 'xanchor':'center', 'yanchor':'top'})
            fig.show()

        elif graph_type == 'bar':
            df = df.sort_values('total', ascending=False)
            fig = px.bar(data_frame=df, x='brawlers', y='total', hover_data=['winrate'], color='winrate')
            fig.update_layout(title={'text': 'Usage Rate per Brawlers ({})'.format(mode), 'y': 0.90, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
            fig.show()

    def plot_brawler_winrate(self, df, mode='global', graph_type='pie'):
        if mode != 'global':
            df = df[df['mode']==mode]
        else:
            df = df.groupby('brawlers').sum()
            df['winrate'] = round(df['wins']*100 / df['total'], 2)
            df.reset_index(inplace=True)
        if graph_type == 'pie':
            fig = px.pie(df, values='winrate', names='brawlers', hover_data=['total'])
            fig.update_layout(title={'text': 'Brawler Usage Rate in {}'.format(mode), 'y': .95, 'x':0.42, 'xanchor':'center', 'yanchor':'top'})
            fig.show()

        elif graph_type == 'bar':
            df = df.sort_values('winrate', ascending=False)
            fig = px.bar(data_frame=df, x='brawlers', y='winrate', hover_data=['total'], color='total')
            fig.update_layout(title={'text': 'Winrate per Brawlers ({})'.format(mode), 'y': 0.90, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
            fig.show()
            
    def plot_mode_usage(self, df, brawlers='ALL', graph_type='pie'):
        if brawlers != 'ALL':
            df = df[df['brawlers']==brawlers]
        else:
            df = df.groupby('mode').sum()
            df['winrate'] = round(df['wins']*100 / df['total'], 2)
            df.reset_index(inplace=True)
        if graph_type == 'pie':
            fig = px.pie(df, values='total', names='mode', hover_data=['winrate'])
            fig.update_layout(title={'text': 'Gamemode Usage Rate for {}'.format(brawlers), 'y': .95, 'x':0.42, 'xanchor':'center', 'yanchor':'top'})
            fig.show()

        elif graph_type == 'bar':
            df = df.sort_values('total', ascending=False)
            fig = px.bar(data_frame=df, x='mode', y='total', hover_data=['winrate'], color='winrate')
            fig.update_layout(title={'text': 'Winrate per Gamemode ({})'.format(brawlers), 'y': 0.90, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
            fig.show()


'''
Find win percentage per gamemode for a player
'''

class BSplayerstats():
    def __init__(self, player_id, df_3v3, headers):
        self.player_id = player_id
        self.df_3v3 = df_3v3
        self.headers = headers 
    
    def init_bl_data(self):
        battle_log_data = []
        for p in self.player_id:
            battle_log_data.append(r.get('https://api.brawlstars.com/v1/players/%23' + p + '/battlelog', headers=self.headers).json())
            if len(battle_log_data) % 150 == 0:
                print ('{} battle logs recorded.'.format(len(battle_log_data)))
        return battle_log_data
    
    def user_id_brawler_list(self):
        battle_log_data = self.init_bl_data()
        #list of brawler id and username 
        user_id = []
        for i in battle_log_data:
            for j in i['items']:
                if 'starPlayer' in j['battle']:
                    for k in j['battle']['teams']:
                        for l in k:
                            user_id.append(l['tag'][1:])                     
        brawler_info = []
        for i in battle_log_data:
            for j in i['items']:
                if 'starPlayer' in j['battle']:
                    for k in j['battle']['teams']:
                        for l in k:
                            brawler_info.append(l['brawler']['name'])
        record = []
        for l in zip(battle_log_data, player_id):
            for j in l[0]['items']:
                if 'starPlayer' in j['battle']:
                    for k in j['battle']['teams']:
                        for q in k:
                            if l[1] in q['tag']:
                                if j['battle']['result'] == 'victory':
                                    record.append(1)
                                    record.append(0)
                                else:
                                    record.append(0)
                                    record.append(1)
        return user_id, brawler_info, record
    
    def make_win_usage(self):
        user_id, brawler_info, record = self.user_id_brawler_list()
        df_winrate = self.df_3v3.groupby('brawlers').sum()
        df_winrate['winrate'] = round(df_winrate['wins'] *100 / df_winrate['total'], 2)
        df_winrate.reset_index(inplace=True)
        winrate = []
        for i in brawler_info:
            winrate.append(df_winrate[df_winrate['brawlers']==i].iat[0,4])

        df_usage = self.df_3v3.groupby('brawlers').sum()
        df_usage['usage'] = np.round(df_usage.groupby('brawlers')['wins'].sum().values * 100 / self.df_3v3['total'].sum(), 2)
        df_usage.reset_index(inplace=True)
        usage = []
        for i in brawler_info:
            usage.append(df_usage[df_usage['brawlers']==i].iat[0,5])

        # cuts into 3's
        winrate = [[winrate[i], winrate[i+1], winrate[i+2]] for i in range(0,len(winrate),3)]
        usage = [[usage[i], usage[i+1], usage[i+2]] for i in range(0,len(usage),3)]

        return winrate, usage
    
    
    def gather_account_info(self):
        user_id, brawler_info, record = self.user_id_brawler_list()
        account_info = []
        for i in user_id:
            temp = r.get('https://api.brawlstars.com/v1/players/%23' + i, headers=self.headers).json()
            account_info.append(temp)
            if len(account_info) % 150 == 0:
                print ('{} account information recorded.'.format(len(account_info)))
        return account_info
    
    def make_Dataframe(self):
        user_id, brawler_info, record = self.user_id_brawler_list()
        account_info = self.gather_account_info()
        stats = []
        items = ['highestTrophies', 'trophies', '3vs3Victories', 'expPoints']
        for i in account_info:
            temp = []
            temp.append(i['name'])
            temp.append(i['tag'])
            for j in items:
                temp.append(i[j])
            stats.append(temp)
        
        # Get winrate and usage rate from top 200
        winrate, usage = self.make_win_usage()

        # List comprehension to combine by 3's
        stats = [stats[i] + stats[i+1] + stats[i+2] for i in range(0,len(stats),3)]
        
        columns = ['name', 'userid', 'highestTrophies', 'trophies', '3vs3Victories', 'expPoints'] * 3
        df = pd.DataFrame(stats, columns=columns)
    
        col = ['winrate'] * 3
        col1 = ['usage'] * 3
        df = pd.concat([df, pd.DataFrame(winrate, columns = col)], axis=1)
        df = pd.concat([df, pd.DataFrame(usage, columns = col1)], axis=1)
        
        df['victory'] = record
        
        return df


if __name__ == "__main__":
    country_code = 'global'
    
    BS = BSdata(country_code, headers)
    df = BS.makeDataframe()


# !curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$self.token"" 'https://api.brawlstars.com/v1/rankings/'$self.country_code'/players'
# !curl -X GET --header 'Accept: application/json' --header "authorization: Bearer "$token"" 'https://api.brawlstars.com/v1/players/%23'$i''