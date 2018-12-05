import numpy as np
import matplotlib.pyplot as plt
from numpy import random as rng
import scipy.stats as stats
from time import localtime, strftime
from basketball_reference_web_scraper import client
from nba_py import team, game, player, constants
from constants import *

year = '2018-19'
fgp = sorted([19,21,15,22,16,19,17,24,21,16,25,26,22,23,11,20,20,27,17])
mean = np.mean(fgp)
std = np.std(fgp)
fit = stats.norm.pdf(fgp, mean, std)
fake_fit = [0.4,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02]
#fitb = ((np.divide(fit,np.sum(fit))))

fig, axs = plt.subplots(1, 1, sharey=True)
axs.plot(fgp,fit, 'k-', lw=2, )
axs.set_xlabel("Field Goals Attemped")
axs.set_ylabel("Probability density")
axs.set_title("Probability Density of Field Goals attempted by Zach Lavine")
plt.savefig("pdf_ZL")

class Player:
    def __init__(self,name,id, year):
        self.name = name
        self.id = id
        self.year = year
        stat = {"FGM":[],'FG3M':[],'FTM':[]}
        t_stats = player.PlayerGameLogs(self.id,league_id='00',season=year, season_type='Regular Season')
        stat_json = t_stats.json['resultSets'][0]['rowSet']
        for i in stat_json:
            stat["FGM"].append(i[7])
            stat["FG3M"].append(i[10])
            stat["FTM"].append(i[13])
        self.stat = stat

    def update(self,FGM,FG3M,FTM):
        self.stat["FGM"].append(FGM)
        self.stat["FG3M"].append(FG3M)
        self.stat['FTM'].append(FTM)
        print(self.stat)

    def instance(self):
        stat = [0,0,0]
        logic = False
        while logic == False:
            i = 0
            for k,v in self.stat.items():
                x = sorted(v)
                mean = np.mean(v)
                std = np.std(v)
                pdf = stats.norm.pdf(x, mean, std)
                pdfb = np.divide(pdf,np.sum(pdf))
                new = rng.choice(x, p = pdfb)
                stat[i] = new
                i += 1
            if stat[0] > stat[1]:
                logic = True
        return stat

team_list = team.TeamList(league_id='00').info()["ABBREVIATION"].values[:30]
print(team_list)
# print(x.stat)

# (x.update(.7,8,1,.5,.75,4))
# print("working: ",constants.TEAMS['CHI']['id'])
# print(team.TeamCommonRoster(1610612741, season= year).roster())

class Team(Player):
    def __init__(self, name, year):
        self.team = name
        self.team_id = constants.TEAMS[name]['id']
        self.year = year
        # self.players = []
        # players = team.TeamCommonRoster(self.team_id, season=year).roster()
        # for i in range(len(players)):
        #     #print(players["PLAYER"][i],players["PLAYER_ID"][i])
        #     self.players.append(Player(players["PLAYER"][i],players["PLAYER_ID"][i],year))

        rec = team.TeamGeneralSplits(self.team_id,season = year).wins_losses()
        self.record = [rec["W"][0],rec["L"][1]]
        self.gamelogs = team.TeamGameLogs(self.team_id,season=year, season_type='Regular Season').info()

    def score(self):
        tfgs = []
        t3fgs = []
        tfts = []
        fgas = []
        fg3as = []
        ftas = []
        log = False
        for i,r,in self.gamelogs.iterrows():
            tfgs.append(r["FG_PCT"])
            t3fgs.append(r["FG3_PCT"])
            fgas.append(r["FGA"])
            fg3as.append(r["FG3A"])
            ftas.append(r["FTA"])
            tfts.append(r["FT_PCT"])


        while log == False:
            t_fg = rng.choice(tfgs)
            t_3fg = rng.choice(t3fgs)
            fga = rng.choice(fgas)
            fg3a = rng.choice(fg3as)
            t_ft = rng.choice(tfts)
            fta = rng.choice(ftas)
            if (fga > fg3a):
                log = True

        score = []
        for i in range(100):
            outcome = rng.choice(["score","miss"], p = [t_fg, 1-t_fg])
            if outcome == "score":
                dec = rng.choice([2,3], p = [(fga-fg3a)/fga, fg3a/fga])
                score.append(dec)
            else:
                score.append(0)
        for i in range(fta):
            oc = rng.choice(["score","miss"], p = [t_ft, 1-t_ft])
            if oc == "score":
                score.append(1)
            else:
                score.append(0)


        return np.cumsum(score)

    def update_rec(self,outcome):
        if outcome  == "W":
            self.record[0] += 1
        else:
            self.record[1] += 1



class Game(Team):
    def __init__(self, home_team, away_team,year):
        self.home = home_team
        self.away = away_team

    def sim(self, plot = False):
        score_home = self.home.score()
        score_away = self.away.score()
        poss1= np.linspace(1,len(score_home),len(score_home))
        poss2= np.linspace(1,len(score_away),len(score_away))
        if plot == True:
            fig = plt.figure()
            axs = fig.add_subplot(111)
            axs.plot(poss1,score_home, label = "{}".format(self.home.team))
            axs.plot(poss2,score_away,label = "{}".format(self.away.team))
            home = constants.TEAMS[self.home.team]['name']
            away = constants.TEAMS[self.away.team]['name']
            axs.set_title("Away:{} vs Home:{}".format(away, home),fontweight="bold")
            axs.legend(loc='lower right')
            axs.set_xlabel("Possesions")
            axs.set_ylabel("Points")
            textfit = r"$\bf{Score}$: %s:%d - %s:%d"%(away,score_away[-1],home,score_home[-1])
            axs.text(0.05, 0.90, textfit, transform=axs.transAxes, fontsize=12,
                    verticalalignment='top')
            plt.savefig("game_vis")


        return (score_home[-1],score_away[-1])


# bulls = Team('CHI',year)
# hawks = Team('ATL',year)
# Game(bulls,hawks, year).sim(plot = True)
# print("SIMULATING....")
# records = []
# for i in range(16,len(team_list)):
#     bulls = Team(team_list[i],year)
#     outcome = "W"
#     num_games = bulls.record[0] + bulls.record[1]
#     print(bulls.team,":",bulls.record)
#     k = 1
#     for j in TEAMS[i][num_games:]:
#         opp = Team(j,year)
#         score = Game(bulls,opp,year).sim()
#         print("game:",k)
#         k+=1
#         if score[0] >= score[1]:
#             outcome = "W"
#         else:
#             outcome = "L"
#         bulls.update_rec(outcome)
#     x = bulls.record
#     records.append(x)
#     print(x)

#print(team.TeamOpponentSplits(1610612741, season = year).by_opponent())
#print(team.TeamGameLogs(1610612741,season=year, season_type='Regular Season').info().loc[0])
