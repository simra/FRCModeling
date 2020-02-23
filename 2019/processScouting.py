import pandas as pd
import csv
import pickle

header = None

teamStats = {}

with open('Scouting/March 23 2019.txt', 'r', encoding='utf-8') as inFile:
    reader = csv.reader(inFile, delimiter='\t')
    for row in reader:
        if header is None:
            header=row
            header = [h.strip() for h in header]
            print(header)
            continue
        row = dict(zip(header,row))
        teamId = 'frc'+row['Team Number']
        if teamId not in teamStats:
            teamStats[teamId]={'matchCount':0}
        teamStats[teamId]['matchCount']+=1
        
        for h in header:
            if "SP-" in h or "CP-" in h:
                #print(h, row[h])
                val=0
                if row[h]=='true':
                    val=1
                elif row[h]=='false':
                    val=0
                else:
                    val=int(row[h])
                if h not in teamStats[teamId]:
                    teamStats[teamId][h]=0
                teamStats[teamId][h]+=val

for t in teamStats:
    for h in teamStats[t]:
        if h!='matchCount':
            teamStats[t][h]/=teamStats[t]['matchCount']

print(teamStats['frc492'])            
with open('scoutingStats.pkl', 'wb') as f:
    pickle.dump(teamStats, f)

        #print(teamId)
        #print(row)
    
    
