import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

lines_df = pd.read_csv(r'lines.csv', delim_whitespace=True)
games_df = pd.read_csv(r'games.csv',delim_whitespace=True)
team_list = pd.read_csv(r'team_list.csv',delim_whitespace=True,header=None)
odds_list = pd.read_csv(r'odds.csv')

def win_chance(line):
    if (line <=0):
        line = abs(line)
        return lines_df['FavoriteWinChance'][line * 2]
    
    else:
        return lines_df['UnderdogWinChance'][line * 2]

def who_wins(AwayTeam, HomeTeam,Prob_Away):

    numberList = [0,1]
    
    if(random.choices(numberList, weights=(Prob_Away, 1-Prob_Away), k=1)[0]):
        return HomeTeam
    else:
        return AwayTeam

def ML_prob(over_prob,under_prob):
    return (1/over_prob)/(1/over_prob + 1/under_prob)



for i in range(games_df.shape[0]):
    if(games_df['AT'][i] != 'at'):
        if(type(games_df['OverUnder'][i]) != int):
            games_df['HomeTeam'][i] = games_df['OverUnder'][i]
        try:
           games_df['Line'][i] = int(games_df['AT'][i][2])
        except:
           games_df['Line'][i] = int(games_df['AT'][i][1])

    if(games_df['AT'][i] == 'at'):
        try:
            games_df['Line'][i] = int(games_df['Line'][i][1:3])
        except:
            try:
                games_df['Line'][i] = float(games_df['Line'][i][1:5])
            except:
                games_df['Line'][i] = int(games_df['Line'][i][1])



games_df = games_df.drop(columns=['AT', 'OverUnder'])

games_df['Prob_Away'] = pd.Series([0.00 for x in range(len(games_df.index))])
games_df['Prob_Home'] = pd.Series([0.00 for x in range(len(games_df.index))])


for i in range(games_df.shape[0]):
    games_df['Prob_Home'][i] = win_chance(games_df['Line'][i])
    games_df['Prob_Away'][i] = 1-win_chance(games_df['Line'][i])


num_sims = 1000

for i in range(num_sims):
    games_df['Season' + str(i+1)] = pd.Series([0 for x in range(len(games_df.index))])
    print(i)
    for j in range(games_df.shape[0]):
        games_df['Season' + str(i+1)][j] = who_wins(games_df['AwayTeam'][j],games_df['HomeTeam'][j],games_df['Prob_Away'][j])

        

for i in range(num_sims):
    team_list['Season' + str(i+1)] = pd.Series([0 for x in range(len(games_df.index))])
    for j in range(team_list.shape[0]):
        wins = games_df['Season' + str(i+1)].value_counts()
        try:
            team_list['Season' + str(i+1)][j] = wins[team_list[0][j]]
        except:
            team_list['Season' + str(i+1)][j] = 0




team_win_list = [team_list.iloc[i].to_list() for i in range(team_list.shape[0])]

odds_list['Prob_over_sims'] = pd.Series([0.00 for x in range(len(odds_list.index))])
odds_list['Prob_under_sims'] = pd.Series([0.00 for x in range(len(odds_list.index))])
odds_list['Prob_over_odds'] = pd.Series([0.00 for x in range(len(odds_list.index))])
odds_list['Prob_under_odds'] = pd.Series([0.00 for x in range(len(odds_list.index))])
odds_list['Prob_difference'] = pd.Series([0.00 for x in range(len(odds_list.index))])
odds_list['Mean_Wins'] = pd.Series([0.00 for x in range(len(odds_list.index))])
odds_list['Standard_deviation'] = pd.Series([0.00 for x in range(len(odds_list.index))])


my_path = os.getcwd()
for i in range(team_list.shape[0]):

    odds_list['Prob_over_sims'].iloc[i] = len([x for x in range(1,num_sims+1) if team_win_list[i][x] > odds_list['OverUnder'].iloc[i]])/num_sims
    odds_list['Prob_under_sims'].iloc[i] = 1 - odds_list['Prob_over_sims'].iloc[i]
    odds_list['Prob_over_odds'].iloc[i] = ML_prob(odds_list['over_odds'].iloc[i], odds_list['under_odds'].iloc[i])
    odds_list['Prob_under_odds'].iloc[i] = 1 - odds_list['Prob_over_odds'].iloc[i]
    odds_list['Prob_difference'].iloc[i] = odds_list['Prob_over_sims'].iloc[i] - odds_list['Prob_over_odds'].iloc[i]
    odds_list['Mean_Wins'].iloc[i] = sum(team_list.iloc[i][1:num_sims])/num_sims
    plt.figure()
    sns.distplot(team_win_list[i][1:num_sims], hist = True, kde = True,bins=len(set(team_list.iloc[i][1:num_sims])),
    color = 'darkblue', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})
    plt.xlabel("Number of wins")
    plt.title(team_win_list[i][0] + " simulated seasons 2021")
    plt.axvline(x=odds_list['Mean_Wins'].iloc[i], color='r')
    plt.savefig(my_path + os.sep + 'Distribution graphs' + os.sep + team_win_list[i][0] + '.png' )


print(2)